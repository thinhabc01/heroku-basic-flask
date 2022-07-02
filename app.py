from flask import Flask, send_file
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>

    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)

@app.route('/return-files/')
def return_files_tut():
	try:
		return send_file('requirements.txt', attachment_filename='requirements.txt')
	except Exception as e:
		return str(e)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

