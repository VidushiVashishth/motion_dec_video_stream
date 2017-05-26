from imageconfig.tempimage import TempImage
import argparse
import warnings
import datetime
import json
import time
import cv2
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import random
import socket, select
from time import gmtime, strftime
from random import randint

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/streaming')
def surveillance():
	
	HOST = '127.0.0.1'
	PORT = 6666
	server_address = (HOST, PORT)

	i = 1
	with open('conf.json') as data_file:
		conf = json.load(data_file)

	warnings.filterwarnings("ignore")
	camera = cv2.VideoCapture(0)

	print "[INFO] warming up..."
	time.sleep(conf["camera_warmup_time"])
	avg = None
	lastUploaded = datetime.datetime.now()
	motionCounter = 0
	Imagecounter = 0

	#fgbg = cv2.BackgroundSubtractorMOG()   // variable background v/s fixed background

	while True:

		(grabbed, frame) = camera.read()
		timestamp = datetime.datetime.now()
		text = "Unoccupied"

		if not grabbed:
			break

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

		if avg is None:
			print "[INFO] starting background model..."
			avg = gray.copy().astype("float")
			continue

		cv2.accumulateWeighted(gray, avg, 0.35)
		frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

		#frameDelta = fgbg.apply(frame)
		thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
			cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)

		cv2.imshow("Security Feed", frame)
  		key = cv2.waitKey(1) & 0xFF

  		# if key == ord("q"):
  		# 	break


		for c in cnts:
			if cv2.contourArea(c) < conf["min_area"]:
				continue

			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # putting rectangles around the detected face
			text = "Occupied"

		ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
		cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.35, (0, 0, 255), 1)

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(server_address)

		if text == "Occupied":

			if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
				motionCounter += 1

				if motionCounter >= conf["min_motion_frames"]:

					t = TempImage(i)
					i = i + 1 
					cv2.imwrite(t.path, frame)
					myfile = open(t.path, 'rb')
					bytes = myfile.read()
					sock.sendall(bytes)
					answer = sock.recv(4096)
					print 'answer = %s' % answer

					if answer == 'GOT IMAGE':
						sock.sendall('BYE BYE')
						print "Image sucessfully sent to the server"

					Imagecounter = Imagecounter + 1
					myfile.close()
					sock.close()


					lastUploaded = timestamp
					motionCounter = 0
		else:

			motionCounter = 0

		if Imagecounter > 2:
			camera.release()
			break

	return "One stream done"

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("80"),
        debug=True
    )
