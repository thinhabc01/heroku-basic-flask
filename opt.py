import base64
import hmac
import unicodedata
import calendar
import datetime, time
import hashlib

from hmac import compare_digest
from urllib.parse import quote, urlencode, urlparse
from typing import Any, Union, Optional, Dict

def build_uri(secret: str, name: str, initial_count: Optional[int] = None, issuer: Optional[str] = None,
              algorithm: Optional[str] = None, digits: Optional[int] = None, period: Optional[int] = None,
              image: Optional[str] = None) -> str:
    # initial_count may be 0 as a valid param
    is_initial_count_present = (initial_count is not None)

    # Handling values different from defaults
    is_algorithm_set = (algorithm is not None and algorithm != 'sha1')
    is_digits_set = (digits is not None and digits != 6)
    is_period_set = (period is not None and period != 30)

    otp_type = 'hotp' if is_initial_count_present else 'totp'
    base_uri = 'otpauth://{0}/{1}?{2}'

    url_args = {'secret': secret}  # type: Dict[str, Union[None, int, str]]

    label = quote(name)
    if issuer is not None:
        label = quote(issuer) + ':' + label
        url_args['issuer'] = issuer

    if is_initial_count_present:
        url_args['counter'] = initial_count
    if is_algorithm_set:
        url_args['algorithm'] = algorithm.upper()  # type: ignore
    if is_digits_set:
        url_args['digits'] = digits
    if is_period_set:
        url_args['period'] = period
    if image:
        image_uri = urlparse(image)
        if image_uri.scheme != 'https' or not image_uri.netloc or not image_uri.path:
            raise ValueError('{} is not a valid url'.format(image_uri))
        url_args['image'] = image

    uri = base_uri.format(otp_type, label, urlencode(url_args).replace("+", "%20"))
    return uri


def strings_equal(s1: str, s2: str) -> bool:
    s1 = unicodedata.normalize('NFKC', s1)
    s2 = unicodedata.normalize('NFKC', s2)
    return compare_digest(s1.encode("utf-8"), s2.encode("utf-8"))

class TOTP():
    def __init__(self, s: str, digits: int = 6, digest: Any = hashlib.sha1, name: Optional[str] = None,
                 issuer: Optional[str] = None, interval: int = 30) -> None:
        self.interval = interval
        self.digits = digits
        self.digest = digest
        self.secret = s
        self.name = name or 'Secret'
        self.issuer = issuer

    def generate_otp(self, input: int) -> str:
        if input < 0:
            raise ValueError('input must be positive integer')
        hasher = hmac.new(self.byte_secret(), self.int_to_bytestring(input), self.digest)
        hmac_hash = bytearray(hasher.digest())
        offset = hmac_hash[-1] & 0xf
        code = ((hmac_hash[offset] & 0x7f) << 24 |
                (hmac_hash[offset + 1] & 0xff) << 16 |
                (hmac_hash[offset + 2] & 0xff) << 8 |
                (hmac_hash[offset + 3] & 0xff))
        str_code = str(code % 10 ** self.digits)
        while len(str_code) < self.digits:
            str_code = '0' + str_code

        return str_code

    def byte_secret(self) -> bytes:
        secret = self.secret
        missing_padding = len(secret) % 8
        if missing_padding != 0:
            secret += '=' * (8 - missing_padding)
        return base64.b32decode(secret, casefold=True)

    @staticmethod
    def int_to_bytestring(i: int, padding: int = 8) -> bytes:
        result = bytearray()
        while i != 0:
            result.append(i & 0xFF)
            i >>= 8
        # It's necessary to convert the final result from bytearray to bytes
        # because the hmac functions in python 2.6 and 3.3 don't work with
        # bytearray
        return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))

    def at(self, for_time: Union[int, datetime.datetime], counter_offset: int = 0) -> str:
        if not isinstance(for_time, datetime.datetime):
            for_time = datetime.datetime.fromtimestamp(int(for_time))
        return self.generate_otp(self.timecode(for_time) + counter_offset)

    def now(self) -> str:
        return self.generate_otp(self.timecode(datetime.datetime.now()))

    def verify(self, otp: str, for_time: Optional[datetime.datetime] = None, valid_window: int = 0) -> bool:
        if for_time is None:
            for_time = datetime.datetime.now()

        if valid_window:
            for i in range(-valid_window, valid_window + 1):
                if strings_equal(str(otp), str(self.at(for_time, i))):
                    return True
            return False

        return strings_equal(str(otp), str(self.at(for_time)))

    def provisioning_uri(self, name: Optional[str] = None, issuer_name: Optional[str] = None,
                         image: Optional[str] = None) -> str:
        return build_uri(self.secret, name if name else self.name,
                               issuer=issuer_name if issuer_name else self.issuer,
                               algorithm=self.digest().name,
                               digits=self.digits, period=self.interval, image=image)

    def timecode(self, for_time: datetime.datetime) -> int:
        if for_time.tzinfo:
            return int(calendar.timegm(for_time.utctimetuple()) / self.interval)
        else:
            return int(time.mktime(for_time.timetuple()) / self.interval)