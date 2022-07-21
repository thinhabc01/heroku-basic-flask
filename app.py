from flask import *
from datetime import datetime
from opt import TOTP

import os
import platform


app = Flask(__name__)

@app.route('/')
def homepage():
	return """
	    <h1>Server OK</h1
	    """
#===========================download file================================
@app.route('/return-files', methods=['GET'])
def return_files_tut():
	try:
		file = str(request.args.get('file'))
		return send_file(file, attachment_filename=file)
	except Exception as e:
		return str(e)
	

	
#========================upload file=====================================
@app.route('/upload')  
def upload():
	return render_template("file_upload_form.html")  
 
@app.route('/success', methods = ['POST'])  
def success():
	if request.method == 'POST':  
		f = request.files['file']  
		f.save(f.filename)  
		return render_template("success.html", name = f.filename)  

#=================================get totp===============================
@app.route('/otp', methods=['GET'] )
def otp():
	code = str(request.args.get('code'))
	totp = TOTP(code)
	return totp.now()

@app.route("/getip", methods=["GET"])
def get_my_ip():
    return request.environ['REMOTE_ADDR']

#===============================chat=====================================
@app.route('/chat')  
def chat():
	with open('dem.txt','r') as f:
    		line = f.read()
		
	d = str(int(line) +1)
	
	with open('dem.txt','w') as f:
    		line = f.write(d)
		
	return d 
#========================================================================



@app.route('/getinfo')
def getinfo():
	s = ""
	arr = os.listdir(os.path.normpath(os.getcwd()))
	for i in arr :
		s +=f"<h1>{str(i)}</h1\n"
	return s

@app.route('/getinfopc')
def getinfopc():
	txt = f"""
	<h1>Machine: {platform.machine()}</h1>
	<h1>Version: {platform.version()}</h1>
	<h1>Plastform: {platform.platform()}</h1>
	<h1>Uname: {platform.uname()}</h1>
	<h1>System: {platform.system()}</h1>
	<h1>Processor: {platform.processor()}</h1>
"""
	return txt


if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)

