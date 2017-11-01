from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route("/")
def hello():
   now = datetime.datetime.now()
   timeString = now.strftime("%Y-%m-%d %H:%M:%S")
   templateData = {
      'title' : 'Welcome to Smart Gateway',
      'time': timeString
      }
   return render_template('main.html',**templateData) #Tempelates/main.html -html file

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True) #Defining IP and port. (Host IP on network)

