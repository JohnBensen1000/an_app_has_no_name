# import requests
# import json
# # from google.cloud import firestore, firebase_admin, messaging
# # from google.cloud import messaging
# import firebase_admin
# from firebase_admin import messaging, credentials

# default_app = firebase_admin.initialize_app()

# serverToken = 'AAAAsEEDk0k:APA91bF1sOQc-E_MFIW9IEDjpELLj3euKlPzAGBfwARrKgX199yD8VrDyx6q5omEkxlzIuK_fU6jb-rAsiRTimhaFtpfq_mXzSZ322PsiMZ65GxFWoIT2lk3ZhwZzJ_Q-MI-E_jMAZo1'
# deviceToken = 'demvJwdFFEJDr0Hg5ioUZ2:APA91bHKtV4seH9RPNryvcdlqiOYxBqjSotewi4Fn_lq56ReogtftIc12gG6J-k0KcZuOk-otYXTdwpPZQOAk6lWkboQemJ1VzOZj6CsiSUqCaxrbJTTErk4AOMOEE18t-vcos2GuEN6'
# # deviceToken = 'dL4crzaRvUSNnKZdu78H1t:APA91bEBLI9x_aiELkpvPSiBUqe7fKJZ_ZIo3OQfPutmwZ53zuJIb7Vwbn13OdYus-qsfg5yh_aRh95UUd_GvLrsjVurN9LOSIKWlJh700U7Lz46kiF5Lqg9ar1_gJKNv8pm6Hp_Vqpc'

# message = messaging.Message(
#     data={
#         'test': 'test'
#     },
#     token=deviceToken,
# )
 
# response = messaging.send(message)
# # print('Successfully sent message:', response)

# # headers = {
# #         'Content-Type': 'application/json',
# #         'Authorization': 'key=' + serverToken,
# #     }

# # body = {
# #         'data': {
# #             'title': 'Sending push form python script',
# #             'body': 'New Message'
# #         },
# #         'to': deviceToken,    
# #     }

# # response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
# # print(response.status_code)

# # print(response.json())