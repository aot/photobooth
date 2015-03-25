#!/usr/bin/python

import RPi.GPIO as GPIO, time, os, subprocess
import pifacedigitalio
def setPrint(arg0):
	decisionFlag = 1
	printDecision = arg0
	print(arg0)

usePiFace = 1

if (usePiFace):
	# PiFace Setup
	pfd = pifacedigitalio.PiFaceDigital() # creates a PiFace Digital object
	#switches
	SWITCH = 0
	BUTTON_PRINT = 1
	
	#leds
	BUTTON_LED = 0
	PRINT_LED = 1
	POSE_LED = 2
	
	print("Photo Booth")
	print("READY...")
	pfd.output_pins[BUTTON_LED].turn_on() # turn on the button LED to begin
	
	gpout = subprocess.check_output("/home/pi/scripts/photobooth/showblank", stderr=subprocess.STDOUT, shell=True)
	while True:
		if (pfd.input_pins[SWITCH].value):
			snap = 0
			while snap < 1:
				print("pose!")
				pfd.output_pins[BUTTON_LED].turn_off()
				pfd.output_pins[POSE_LED].turn_on()
				time.sleep(0.1)
				for i in range(5):
					pfd.output_pins[POSE_LED].turn_off()
					time.sleep(0.4)
					pfd.output_pins[POSE_LED].turn_on()
					time.sleep(0.4)
				for i in range(5):
					pfd.output_pins[POSE_LED].turn_off()
					time.sleep(0.1)
					pfd.output_pins[POSE_LED].turn_on()
					time.sleep(0.1)
				pfd.output_pins[POSE_LED].turn_off()
				print("SNAP")
				#gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename /home/pi/photobooth_images/temp/photobooth%H%M%S.jpg", stderr=subprocess.STDOUT, shell=True)
				gpout = subprocess.check_output("/home/pi/scripts/photobooth/photocapture", stderr=subprocess.STDOUT, shell=True) #gphoto2 cannot save to external partition so using script to manually move file
				print(gpout)
				if "ERROR" not in gpout: 
					snap += 1
				
				pfd.output_pins[POSE_LED].turn_off()
				time.sleep(0.5)
			#print(gpout)
			#print(gpout[2])
			time.sleep(5)
			print("Print photo?")
			#listener = pifacedigitalio.InputEventListener(chip=pfd)
			#listener2 = pifacedigitalio.InputEventListener(chip=pfd)
			#listener.register(BUTTON_PRINT, pifacedigitalio.IODIR_FALLING_EDGE, setPrint(1));
			#listener2.register(SWITCH, pifacedigitalio.IODIR_FALLING_EDGE, setPrint(0));
			#listener.activate()
			#listener2.activate()
			#Request print
			decisionFlag = 0
			pfd.output_pins[PRINT_LED].turn_on()
			pfd.output_pins[BUTTON_LED].turn_on()
			printDecision = 0
			while(decisionFlag == 0):
				if (pfd.input_pins[BUTTON_PRINT].value):
					decisionFlag = 1
					printDecision = 1
				if (pfd.input_pins[SWITCH].value):
					decisionFlag = 1
	
				#time.sleep(0.25)
			pfd.output_pins[PRINT_LED].turn_off()
                        pfd.output_pins[BUTTON_LED].turn_off()
			print("OK...")
			#listener.deactivate()
			#listener2.deactivate()
			if(printDecision):
				pfd.output_pins[PRINT_LED].turn_on()
				print("printing")
				gpout = subprocess.call("/home/pi/scripts/photobooth/printphoto", shell=True)
				pfd.output_pins[PRINT_LED].turn_on()
				print(gpout)
				time.sleep(60)
			else:
				gpout = subprocess.call("/home/pi/scripts/photobooth/copyphoto", shell=True)
			print("RESTARTING")
			# TODO: implement a reboot button
			# Wait to ensure that print queue doesn't pile up
			# TODO: check status of printer instead of using this arbitrary wait time
			#time.sleep(110)
			time.sleep(5)
			gpout = subprocess.check_output("/home/pi/scripts/photobooth/showblank", stderr=subprocess.STDOUT, shell=True)
			print("READY...")
			pfd.output_pins[PRINT_LED].turn_off()
			pfd.output_pins[BUTTON_LED].turn_on()
	
else:

	# GPIO setup
	GPIO.setmode(GPIO.BCM)
	SWITCH = 24
	GPIO.setup(SWITCH, GPIO.IN)
	RESET = 25
	GPIO.setup(RESET, GPIO.IN)
	PRINT_LED = 22
	POSE_LED = 18
	BUTTON_LED = 23
	GPIO.setup(POSE_LED, GPIO.OUT)
	GPIO.setup(BUTTON_LED, GPIO.OUT)
	GPIO.setup(PRINT_LED, GPIO.OUT)
	GPIO.output(BUTTON_LED, True)
	GPIO.output(PRINT_LED, False)

	while True:
	  if (GPIO.input(SWITCH)):
		snap = 0
		while snap < 4:
			print("pose!")
			GPIO.output(BUTTON_LED, False)
			GPIO.output(POSE_LED, True)
			time.sleep(1.5)
			for i in range(5):
				GPIO.output(POSE_LED, False)
				time.sleep(0.4)
				GPIO.output(POSE_LED, True)
				time.sleep(0.4)
			for i in range(5):
				GPIO.output(POSE_LED, False)
				time.sleep(0.1)
				GPIO.output(POSE_LED, True)
				time.sleep(0.1)
			GPIO.output(POSE_LED, False)
			print("SNAP")
			gpout = subprocess.check_output("gphoto2 --capture-image-and-download --filename /home/pi/photobooth_images/photobooth%H%M%S.jpg", stderr=subprocess.STDOUT, shell=True)
			print(gpout)
			if "ERROR" not in gpout: 
				snap += 1
			GPIO.output(POSE_LED, False)
			time.sleep(0.5)
		print("please wait while your photos print...")
		GPIO.output(PRINT_LED, True)
		# build image and send to printer
		subprocess.call("sudo /home/pi/scripts/photobooth/assemble_and_print", shell=True)
		# TODO: implement a reboot button
		# Wait to ensure that print queue doesn't pile up
		# TODO: check status of printer instead of using this arbitrary wait time
		time.sleep(110)
		print("ready for next round")
		GPIO.output(PRINT_LED, False)
		GPIO.output(BUTTON_LED, True)
