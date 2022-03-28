import ssl
import smtplib
import json
import os

port    = 465 
context = ssl.create_default_context()

def send_email(bodyDict):
    print(bodyDict)
    pass
    # emailString = os.getenv("ENVIRONMENT") + '\n'
    # for key, value in bodyDict.items():
    #     emailString += key + ': ' + value + '\n'

    # with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    #     server.login("entropy.developer1@gmail.com", "tHis@@Is6**9nOt_-me")
    #     server.sendmail(
    #         "entropy.developer1@gmail.com", 
    #         "entropy.developer1@gmail.com", 
    #         emailString
    #     )