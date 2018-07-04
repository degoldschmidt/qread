# USAGE
# python barcode_scanner_video.py

# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import pygame
pygame.init()
pygame.mixer.music.load('beep.mp3')

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
	help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True,resolution=(500, 500) ).start()
time.sleep(2.0)

# open the output CSV file for writing and initialize the set of
# barcodes found thus far
csv = open(args["output"], "w")
found = set()
detect = False

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it to
	# have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=500, height=500)

	# find the barcodes in the frame and decode each of the barcodes
	barcodes = pyzbar.decode(frame)

	# loop over the detected barcode
	if not detect:
	    for barcode in barcodes:
	        # extract the bounding box location of the barcode and draw
	        # the bounding box surrounding the barcode on the image
	        (x, y, w, h) = barcode.rect
	        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)

	        # the barcode data is a bytes object so if we want to draw it
	        # on our output image we need to convert it to a string first
	        barcodeData = barcode.data.decode("utf-8").encode('ascii','ignore')
	        barcodeType = barcode.type
	        print(barcodeData, barcodeType)
	        pygame.mixer.music.play(0)
	        detect = True
	        detect_time = time.time()

	        # draw the barcode data and barcode type on the image
	        text = "{}".format(barcodeData)
	        cv2.putText(frame, text, (x, y - 10),
	                cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 255), 1)

	        # if the barcode text is currently not in our CSV file, write
	        # the timestamp + barcode to disk and update the set
	        if barcodeData not in found:
	            csv.write("{},{}\n".format(datetime.datetime.now(), barcodeData))
	            csv.flush()
	            found.add(barcodeData)
        else:
            if time.time()-detect_time > 10.:
            	detect = False

	# show the output frame
	cv2.imshow("Barcode Scanner", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
csv.close()
cv2.destroyAllWindows()
vs.stop()
