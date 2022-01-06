# ****************************************************
# * File         : GarduinoAWS.py
# * Description  : connecting to AWS IOT and posting the data from the sensors
# * Author       : Rowland Marshall
# * 
# * Versions     :
# *     0.03 | 2020-08-06 18:45:01 | Added in Row and Pos so that messages can be processed into DynamoDB on the other side
# *                                  Changed str references to int and float depending on the type
# *     0.02 | 2020-08-05 17:18:47 | Reshaped to match the proper data coming in but it doesn't read from GarduinoBase yet...just static values.
# *                                  Added in voltage values; normal temp value
# *     0.01 | 2020-08-05 11:19:46 | Initial build for learning how to connect - it doesn't read data but just sends values that will trigger an email
# *                                 Initial code provided from the tutorial https://docs.aws.amazon.com/iot/latest/developerguide/iot-moisture-raspi-setup.html
# ****************************************************/


#from adafruit_seesaw.seesaw import Seesaw
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
#from board import SCL, SDA

import logging
import time
import json
import argparse
#import busio

# Shadow JSON schema:
#
# {
#   "state": {
#       "reported":{
#           "row": <STRING>,
#           "pos": <STRING>,
#           "moistureV":<FLOAT VALUE>,
#           "moistureLevel":<INT VALUE>,
#           "lightV":<FLOAT VALUE>,
#           "lightLevel":<INT VALUE>,
#           "tempV":<FLOAT VALUE>,
#           "tempC":<FLOAT VALUE>,
#       }
#   }
# }


# Test example
# post to: $aws/things/Garduino/shadow/update/accepted    
# identify the device based on the position in the garden (this one will be row 0, position 0)
# {
#     "state": {
#         "reported":{ 
#             "row": "0",
#             "pos": "0",
#             "moistureV": 3.00,
#             "moistureLevel": 350,
#             "lightV": 2.70,
#             "lightLevel": 300,
#             "tempV": 2.50,
#             "tempC": 29.43
#         }
#     }
# }

# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("Row: " + str(payloadDict["state"]["reported"]["row"]))
        print("Pos: " + str(payloadDict["state"]["reported"]["pos"]))
        print("moisture: " + str(payloadDict["state"]["reported"]["moistureV"]))
        print("moistureLevel: " + str(payloadDict["state"]["reported"]["moistureLevel"]))
        print("Light: " + str(payloadDict["state"]["reported"]["lightV"]))
        print("LightLevel: " + str(payloadDict["state"]["reported"]["lightLevel"]))
        print("temperatureV: " + str(payloadDict["state"]["reported"]["tempV"]))
        print("temperatureC: " + str(payloadDict["state"]["reported"]["tempC"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

# Function called when a shadow is deleted
def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


# Read in command-line parameters
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    return args


# Configure logging
# AWSIoTMQTTShadowClient writes data to the log
def configureLogging():

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


# Parse command line arguments
args = parseArgs()

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)

# If no --port argument is passed, default to 8883
if not args.port: 
    args.port = 8883


# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(args.clientId)
myAWSIoTMQTTShadowClient.configureEndpoint(args.host, args.port)
myAWSIoTMQTTShadowClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)

# AWSIoTMQTTShadowClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5) # 5 sec

# Initialize Raspberry Pi's I2C interface
#i2c_bus = busio.I2C(SCL, SDA)

# Intialize SeeSaw, Adafruit's Circuit Python library
#ss = Seesaw(i2c_bus, addr=0x36)

print("initialised ok") # debug
print(args.clientId)
# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

print("connect ok")
# Create a device shadow handler, use this to update and delete shadow document
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(args.thingName, True)

# Delete current shadow JSON doc
deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

# Read data from moisture sensor and update shadow
while True:
    # identify the device based on the position in the garden (this one will be row 0, position 0)
    row = 3
    pos = 0

    # read moisture level through capacitive touch pad
    moistureV = 3.00
    moistureLevel = 350

    # read light level 
    lightV = 2.70
    lightLevel = 300

    # read temperature from the temperature sensor
    tempV = 2.50
    tempC = 29.43

    # Display moisture and temp readings
    print("Row: {}".format(row))
    print("Position: {}".format(pos))
    print("Moisture (V): {}".format(moistureV))
    print("Moisture Level (V): {}".format(moistureLevel))
    print("Light (V): {}".format(lightV))
    print("Light Level (V): {}".format(lightLevel))
    print("Temperature (V): {}".format(tempV))
    print("Temperature (C): {}".format(tempC))
    
    # Create message payload
    payload = {"state":{"reported":{"row":str(row), "pos":str(row), "moistureV":float(moistureV),"moistureLevel":int(moistureLevel),"lightV":float(lightV),"lightLevel":int(lightLevel),"tempV":float(tempV),"tempC":float(tempC)}}}

    # Update shadow
    deviceShadowHandler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)
    time.sleep(10)