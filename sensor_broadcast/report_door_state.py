import pika
import sys
import RPi.GPIO as GPIO
import datetime
import requests
import ConfigParser

change_url = 'http://fridge-cop.appspot.com/change_state?new_state={0}&state_update_key={1}'
current_state = None

config = ConfigParser.ConfigParser()
config.read("secure_keys.ini")
state_update_key = config.get("secure_keys", "state_update_key")
print("Key loaded: " + state_update_key)

def main():
	current_state = ContainerState.UNKNOWN
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(7, GPIO.BOTH, callback=detected_open)

	while True:
        	pass

def detected_open(channel):
	value = GPIO.input(7)
	print(value)
	if (value == 1):
		new_state = ContainerState.OPEN
	elif (value == 0):
		new_state = ContainerState.CLOSED
	else:
		new_state = ContainerState.UNKNOWN

	print("state: " + str(new_state) + " " + str(datetime.datetime.now()))
	report_state_change(new_state)

def report_state_change(new_state, retries = 0):
	try:
		res = requests.get(change_url.format(new_state, state_update_key))
	except (requests.ConnectionError, requests.RequestException, requests.HTTPError):
		if ((new_state == ContainerState.CLOSED) and (retries < 30)): #we need to keep retrying, can't leave the fridge open!
                	print("Retrying, looks like we lost internet :(")
                        time.sleep(5)
                	report_state_change(new_state, retries + 1)

class ContainerState:
        OPEN = 1
        CLOSED = 2
        UNKNOWN = 3
        TRANSITION = 4

if __name__ == "__main__":
    main()

