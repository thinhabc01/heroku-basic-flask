from flask import *
from datetime import datetime
from opt import TOTP

import os
import platform
import psutil

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
		s +=f"<h1>{str(i)}</h1>\n"
	return s

@app.route('/getinfopc')
def getinfopc():
	_os,_bit = platform.architecture()
	_memory = psutil.virtual_memory().total
	txt = f"""
	<h1><a href="/" class="home">Home Page</a></h1>
	<h3>Machine: {platform.architecture()}</h3>
	<h3>System: {platform.system()}</h3>
	<h3>Ram: {round(psutil.virtual_memory().total/1073741824, 4)} GB</h3>
"""
	return txt


if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)

