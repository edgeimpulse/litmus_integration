import json
import subprocess, sys

subprocess.call('pip install requests -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')

import time, hmac, hashlib, requests

# Customize this with the hmac and API key from your Edge Impulse project
hmac_key = "<YOUR_HMAC>"
API_KEY = "<YOUR_API_KEY>"

# Customize this dictionary to reflect your list of sensors
whitelist_sensors = [
    { 
        "name": "FaultCode_L2_Min_Value",
        "units": "tbd"
    },
    { 
        "name": "CycleTime_Base",
        "units": "tbd"
    },
    { 
        "name": "Current",
        "units": "tbd"
    },
    { 
        "name": "Speed",
        "units": "tbd"
    },
    { 
        "name": "FaultCode_L2",
        "units": "tbd"
    },
    { 
        "name": "CycleStarted",
        "units": "tbd"
    },
    { 
        "name": "FaultCode_Min_Value",
        "units": "tbd"
    },
    { 
        "name": "Pressure",
        "units": "tbd"
    },
    { 
        "name": "Level_PV",
        "units": "tbd"
    },
    { 
        "name": "QualityCode_Scrap_Min",
        "units": "tbd"
    },
    { 
        "name": "Temperature_PV",
        "units": "tbd"
    },
    { 
        "name": "Pressure_SP",
        "units": "tbd"
    },
    { 
        "name": "Step1",
        "units": "tbd"
    },
    { 
        "name": "Step3",
        "units": "tbd"
    },
    { 
        "name": "Voltage",
        "units": "tbd"
    },
    { 
        "name": "FaultCode_Max_Value",
        "units": "tbd"
    },
    { 
        "name": "TaktTime_Variation_Factor",
        "units": "tbd"
    },
    { 
        "name": "Downtime_Variation_Factor",
        "units": "tbd"
    },
    { 
        "name": "Level_SP",
        "units": "tbd"
    },
    { 
        "name": "TaktTime_Base",
        "units": "tbd"
    },
    { 
        "name": "Temperature",
        "units": "tbd"
    },
    { 
        "name": "Step5",
        "units": "tbd"
    },
    { 
        "name": "ReasonCode_Min",
        "units": "tbd"
    },
    { 
        "name": "ReasonCode_L2_Max",
        "units": "tbd"
    },
    { 
        "name": "QualityCode_Scrap_Max",
        "units": "tbd"
    },
    { 
        "name": "isFaulted",
        "units": "tbd"
    },
    { 
        "name": "GoodPart",
        "units": "tbd"
    },
    { 
        "name": "Step4",
        "units": "tbd"
    },
    { 
        "name": "Temperature_SP",
        "units": "tbd"
    },
    { 
        "name": "CycleTime_Variation_Factor",
        "units": "tbd"
    },
    { 
        "name": "FaultCode_L2_Max_Value",
        "units": "tbd"
    },
    { 
        "name": "FaultOccurrenceFactor",
        "units": "tbd"
    },
    { 
        "name": "PartMade",
        "units": "tbd"
    },
    { 
        "name": "Step2",
        "units": "tbd"
    },
    { 
        "name": "Pressure_PV",
        "units": "tbd"
    },
    { 
        "name": "FaultCode",
        "units": "tbd"
    },
    { 
        "name": "BadPart",
        "units": "tbd"
    },
    { 
        "name": "ReasonCode_Max",
        "units": "tbd"
    },
    { 
        "name": "ReasonCode_L2_Min",
        "units": "tbd"
    },
    { 
        "name": "BadPartInterval_Base",
        "units": "tbd"
    },
    { 
        "name": "BadPartInterval_Variation",
        "units": "tbd"
    }    
]

def lambda_handler(event, context):
    print("RAW:: ",event)    
    full_sensors = process(event)
    full_sensors = sign_payload(full_sensors)
    print("Processed: ",full_sensors)
    if len(full_sensors.get("payload").get("sensors")) < 1:
        print("No messages found to upload")
    else:
        print("Uploading ",len(full_sensors)," messages")
        print(full_sensors)
        output = upload_sample(full_sensors)

    # TODO implement
    return {
        'statusCode': 200,
        # 'body': json.dumps(f"Found tagName {tagName}, with value {value}")
        'body': json.dumps(event)
        # 'body': json.dumps(keyString)
    }
    
def cast_to_numeric(data):
#  print("Input data: ",data)
  if (data == None) | (data == "null"):
    data = 0

  if isinstance(data, (int, float)):
    return data
  else:
    if data.isdigit():
        return int(data)
    try:
        return float(data)
    except ValueError:
        return data  # Return the original string if it's not a number

        
def upload_sample(data):
 
    encoded = json.dumps(data)
    # print("Encoded: ",encoded)
    stamp = round(time.time() * 1000)
    filename = f"litmus_upload_{stamp}.json"

    res = requests.post(url='https://ingestion.edgeimpulse.com/api/training/data',
                        data=encoded,
                        headers={
                            'Content-Type': 'application/json',
                            'x-no-label': '1',
                            'x-file-name': filename,
                            'x-api-key': API_KEY
                        })
    if (res.status_code == 200):
        print('INFO: Uploaded file to Edge Impulse', res.status_code, res.content)
    else:
        print('ERROR: Failed to upload file to Edge Impulse', res.status_code, res.content)

def sign_payload(payload): 

    encoded = json.dumps(payload)

    # sign message
    signature = hmac.new(bytes(hmac_key, 'utf-8'), msg = encoded.encode('utf-8'), digestmod = hashlib.sha256).hexdigest()
    # print("Signature: ",signature)

    # set the signature again in the message, and encode again
    payload['signature'] = signature

    return payload

# The main processing method
# This takes in a full message JSON
# Then parses it into a CBOR format
def process(example):
    # print("RAW: ", example)
    print("Number of Messages: ",len(example))
    unique_sensors = []
    sensor_values = {}
    print(type(example))

    for message in example:

        timestamp = message.get("timestamp")
        tagname = message.get("tagName")
        if tagname not in unique_sensors:
            sensor_entry = {
                "name" : tagname,
                "units" : "tbd"
            }
            unique_sensors.append(sensor_entry)
        value = cast_to_numeric(message.get("value"))

        if timestamp not in sensor_values:
            current_sample = {}
            current_sample[tagname] = value
            sensor_values[timestamp] = current_sample
        else:
            # get the current list of values, and then append this
            current_sample = sensor_values.get(timestamp)    
            current_sample[tagname] = value
            sensor_values[timestamp] = current_sample

    output_data = {}
    protected = {
        "ver": "v1",
        "alg": "HS256",
        "iat": 1694120518.279886
    }
    payload = {}
    payload["device_name"] = "NODEVICE"
    payload["device_type"] = "NODEVICETYPE"
    payload["interval_ms"] = 1000
    payload["sensors"] = whitelist_sensors
 
    output_data["protected"] = protected

    # print("Sensor values length: ",len(sensor_values))
    output_data_values = []
    for timestamp in sensor_values:
        values = []
        # print("SV key",timestamp)
        sensor_map = sensor_values.get(timestamp)
        #print("Found sensor map of type",type(sensor_map))
        # iterate through the defined sensor values
        # we do this to make sure that we have a well-formed grid of data, with the same 
        # features in the same places
        print("Found ",len(whitelist_sensors)," sensors.") 
        for sensor_name in whitelist_sensors:
            #print("Loading value for sensor: ",sensor_name," of type ",type(sensor_name))
            sensor_val = sensor_map.get(sensor_name.get("name"))
            # print("Value: ",sensor_val)
            if (sensor_val is None):
                # print("Found null sensor value")
                sensor_val = 0.0
            values.append(sensor_val)
        output_data_values.append(values)
        print("Found ",len(values)," values.") 


    payload["values"] = output_data_values
    output_data["payload"] = payload

    return output_data
