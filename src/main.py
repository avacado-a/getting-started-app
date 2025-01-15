from flask import Flask, render_template, request, redirect, url_for, abort, send_file, jsonify
import flask as werkzeug
from os import environ
import random
from random import choice
import time
import requests
import os
import cv2
from matplotlib.figure import Figure
import base64
from io import BytesIO
file = open("src/save.txt","r")
db = eval(file.read())
file.close()
def plotsave():
  global db
  db["saveS"][int(time.strftime("%Y%m"))] = db["scoreS"]
  db["saveT"][int(time.strftime("%Y%m"))] = db["scoreT"]
  db["saveS"] = dict(sorted(db["saveS"].items()))
  db["saveS"] = dict(sorted(db["saveS"].items()))
  xS = [str(i) for i in list(db["saveS"])]
  yS = [db["saveS"][i] for i in list(db["saveS"])]
  xT = [str(i) for i in list(db["saveT"])]
  yT = [db["saveT"][i] for i in list(db["saveT"])]
  file = open("src/save.txt","w")
  file.write(str(db))
  file.close()
  return [xS,yS,xT,yT]
def isinmonth(lastsecepoch):
  last = time.gmtime(lastsecepoch)
  now = time.gmtime()
  if now.tm_year == last.tm_year:
    if now.tm_mon == last.tm_mon:
      return True
  return False
def check():
  global db
  if not isinmonth(db["time"]):
    db["saveS"][int(time.strftime("%Y%m"))] = db["scoreS"]
    db["saveT"][int(time.strftime("%Y%m"))] = db["scoreT"]
    db["scoreS"] = 0
    db["scoreT"] = 0
  db["time"] = time.time()
  file = open("src/save.txt","w")
  file.write(str(db))
  file.close()

app = Flask(__name__)

@app.before_request
def before_request():
  time.sleep(0.5)


@app.route("/")
def home():
  #try:
  #  os.remove("static/assets/plot.jpg")
  #except Exception as e:
  # print("Error: "+str(e),"passed")
  check()
  xS,yS,xT,yT = plotsave()
  fig = Figure()
  ax = fig.subplots()
  if len(xS) in [0,1]:
    ax.scatter(xS,yS)
  else:
    ax.plot(xS,yS)
  buf = BytesIO()
  fig.savefig(buf, format="png")
  data = base64.b64encode(buf.getbuffer()).decode("ascii")
  fig = Figure()
  ax = fig.subplots()
  if len(xS) in [0,1]:
    ax.scatter(xT,yT)
  else:
    ax.plot(xT,yT)
  buf = BytesIO()
  fig.savefig(buf, format="png")
  data1 = base64.b64encode(buf.getbuffer()).decode("ascii")
  
  return f"""
  <!doctype html>
    <html>
    <head>
    <script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.0.1.min.js"></script>
    <link href="/static/css/all.css" rel="stylesheet" type="text/css" />
    <link rel="shortcut icon" href="/static/assets/favicon.ico" type="image/x-icon">
    </head>
    <body>
  <h1>Anger Counter</h1>
  <a href={url_for("sidh")}?score=0><button>SIDH</button></a>
  <a href={url_for("tanay")}?score=0><button>TANAY</button></a>
  <h2>Sidh:</h2>
  <img src='data:image/png;base64,{data}'/>
  <h2>Tanay:</h2>
  <img src='data:image/png;base64,{data1}'/>
</body>
</html>"""

@app.route("/sidh")
def sidh():
  global db
  score = int(request.args.get('scores',0))
  db["scoreS"] += score
  print(db["scoreS"])
  return render_template("sidh.html", scores = db["scoreS"])
@app.route("/tanay")
def tanay():
  global db
  score = int(request.args.get('scores',0))
  db["scoreT"] += score
  print(db["scoreT"])
  return render_template("tanay.html", scores = db["scoreT"])

@app.route('/capture', methods=['POST'])
def capture():
    image_data = request.files['image'].read()
    cv2_image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    cv2.imwrite("src/static/letsgo.png",cv2_image)
    return jsonify({'success': True})

@app.route('/show')
def show():
    return send_file("/workspaces/Web-Based-Webcam/src/static/letsgo.png")



@app.route('/cam')
def hello_world():
    return """
<!DOCTYPE html>
<html>
<head>
    <link rel="icon" type="image/png" href="/static/lgo.png"> 
</head>
<body>
    <video id="video" autoplay></video>
    <canvas id="canvas" width="640" height="480"></canvas>
    <script>
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let bounded = document.getElementById('bounded');
        let detection = document.getElementById('detection');
        var width = 640;
        var height = 480;
        navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 4000 },//{ ideal: 1920 },
                        height: { ideal: 4000 },//{ ideal: 1080 }
                        facingMode: { exact: "user" }
                    }
                })
                .then(function(stream) {
                video.srcObject = stream;
                video.onloadedmetadata = () => {
                    width = video.videoWidth;
                    height = video.videoHeight;
                    video.width = width.toString();
                    video.height = height.toString();
                    canvas.width = width.toString();
                    canvas.height = height.toString();
                    console.log(`Webcam image size: ${width} x ${height}`);
                };
            })
            .catch(function(error) {
                console.error('Error accessing media devices.', error);
            });
        function check() {
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(function(blob) {
                const formData = new FormData();
                formData.append('image', blob, 'letsgo.png'); // Adjust filename as needed
                fetch('/capture', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        console.log('Image saved successfully!');
                    } else {
                        console.log('Error saving image');
                    }
                })
                .catch(error => {
                    console.error('Error sending image:', error);
                });
            });
        }
        var t=setInterval(check,1000*0.05);
    </script>
</body>
</html>"""



app.run(host="0.0.0.0",port=8080)#(host='0.0.0.0', port=8080, debug=True,use_reloader=False)
