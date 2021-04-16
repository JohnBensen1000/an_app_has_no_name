import requests
import json

serverToken = 'AAAALGfgH5A:APA91bH1FgqgJOZ4LQds7XgnRxatrIxZgP9hzvx8MItG8fsgxDGAgR9XocFWh8qwNfCxBaj-eddA5DwS2r2SNRbNU2iOIJvu-QaXo_2aPf-DujhqdMhz9H3aW5ZItBfXuV0JZ5BGQXDV'
deviceToken = 'fRXbqWFYdUPEkAqq6cRjA5:APA91bGKN5b6P0PWNBpPXRhXoVIS_luUBMBrWMcU61tZzE24TZpm47mSTm4TyrfMcZPFMCBfzI_IYIO1qPeRJv_26wYSfzfLHBguJQ5v-eGnAOfLvqj013SSSQOdNY75Tv2Eg10YCE-l'

headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
      }

body = {
          'notification': {'title': 'Sending push form python script',
                            'body': 'New Message'
                            },
          'to':
              deviceToken,
          'priority': 'high',
        #   'data': dataPayLoad,
        }
response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
print(response.status_code)

print(response.json())