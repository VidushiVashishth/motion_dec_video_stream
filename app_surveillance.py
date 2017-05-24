from tempimage import TempImage
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

HOST = '127.0.0.1'
PORT = 6666

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
sock.connect(server_address)

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/streaming')
def surveillance():

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

  	if key == ord("q"):
  	    break

		
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

<<<<<<< HEAD
	    if text == "Occupied":
		print("In 1st if")

		if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
		    motionCounter += 1
		    print("In 2nd if")

		    if motionCounter >= conf["min_motion_frames"]:
			print("In 3rd if")

			t = TempImage(i)
			cv2.imwrite(t.path, frame)
			lastUploaded = timestamp
			motionCounter = 0  
			# file = os.path.join(os.path.relpath(__main__), str(t.path))
			#file = t
			#i = i+1
			#myfile = open(file, 'rb')
			#bytes = cv2.imread(t.path, 1)
			#bytes = myfile.read()
			#print(bytes)
    			#bytes = myfile.read()
                        #sock.sendall(bytes)
    				

        		# check what server send
        		#answer = sock.recv(4096)
        		#print 'answer = %s' % answer
                                        
                        #if answer == 'GOT IMAGE' :
        		   # print("In the 4th if")
        		  #  sock.sendall("BYE BYE ")
        		 #   print 'Image successfully send to server'

        		#else:
        		 #   print("In 4th if else")
        		    
        		#myfile.close()

                    else: print "In 3rd if else"
       	        else: print "In 2nd if else"
=======
		if text == "Occupied":
			print("In 1st if")

			if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
				motionCounter += 1
				print("In 2nd if")

				if motionCounter >= conf["min_motion_frames"]:
					print("In 3rd if")

					t = TempImage(i)
					cv2.imwrite(t.path, frame)
					lastUploaded = timestamp
					motionCounter = 0  
					# file = os.path.join(os.path.relpath(__main__), str(t.path))
					file = t
					i = i+1
					# myfile = open(file, 'rb')
					bytes = cv2.imread(t, 1)
					# bytes = myfile.read()
					print(bytes)
    				#bytes = myfile.read()
    					sock.sendall(bytes)
    				

        			# check what server send
        				answer = sock.recv(4096)
        				print 'answer = %s' % answer

        				if answer == 'GOT IMAGE' :
        					print("In the 4th if")
        					sock.sendall("BYE BYE ")
        					print 'Image successfully send to server'

        				else:
        					print("In 4th if else")
        			
        			myfile.close()
>>>>>>> 1ea117043ea2809b1488e891ed65516aeb95eeab

    	    else:
  	        print("In 1st if else")
  		motionCounter = 0

  		    
    return

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("7772"),
        debug=True
    )
