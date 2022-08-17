# get 2fa

import base64
import hmac
import calendar
import datetime, time
import hashlib

def _timecode(for_time: datetime.datetime, interval: int = 30) -> int:
        if for_time.tzinfo:
            return int(calendar.timegm(for_time.utctimetuple()) / interval)
        else:
            return int(time.mktime(for_time.timetuple()) / interval)

def _byte_secret(secret) -> bytes:
        secret = secret
        missing_padding = len(secret) % 8
        if missing_padding != 0:
            secret += '=' * (8 - missing_padding)
        return base64.b32decode(secret, casefold=True)

def _int_to_bytestring(i: int, padding: int = 8) -> bytes:
        result = bytearray()
        while i != 0:
            result.append(i & 0xFF)
            i >>= 8
        return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))

def get_2fa(secret: str) -> str:
        time_code = _timecode(datetime.datetime.now())
        hasher = hmac.new(_byte_secret(secret), _int_to_bytestring(time_code), hashlib.sha1)
        hmac_hash = bytearray(hasher.digest())
        offset = hmac_hash[-1] & 0xf
        code = ((hmac_hash[offset] & 0x7f) << 24 |
                (hmac_hash[offset + 1] & 0xff) << 16 |
                (hmac_hash[offset + 2] & 0xff) << 8 |
                (hmac_hash[offset + 3] & 0xff))
        str_code = str(code % 10 ** 6)
        while len(str_code) < 6:
            str_code = '0' + str_code

        return str_code
