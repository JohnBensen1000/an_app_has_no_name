import sys
import json 

from typing import cast
from google.cloud import firestore
from firebase_admin import messaging

from models.models import User, Post

db = firestore.Client()

def _upload_activity(user, activity):
    activity['time']  = firestore.SERVER_TIMESTAMP
    activity['isNew'] = True

    docRef = db.collection('ACTIVITY').document(user.uid).collection('activity').document()
    docRef.set(activity)

    user.isUpdated = False
    user.save()

def _send_push_notification(user, notification, type, data={}):
    try:
        if user.deviceToken != None and user.deviceToken != '':
            message = messaging.Message(
                notification = messaging.Notification(
                    title = notification
                ),
                data = {
                    'newActivity': 'True',
                    'type': type,
                    'data': json.dumps(data)
                }, 
                token=user.deviceToken
            )
            messaging.send(message)
    except:
        print(" [MESSAGING ERROR]", sys.exc_info())

def add_new_comment(postID, commenterUid):
    commenter = User.objects.get(uid=commenterUid)
    post      = Post.objects.get(postID=postID)
    user      = post.creator

    activity = {
        'type': 'comment',
        'data': {
            'post':      post.to_dict(),
            'commenter': commenter.to_dict(),
        }
    }

    _upload_activity(user, activity)
    _send_push_notification(
        user, 
        commenter.username + " commented on your post!",
        'comment',
        data={"post": post.to_dict()}
    )

def add_new_follower(user, follower):
    activity = {
        'type': 'new_follower',
        'data': {
            'follower': follower.to_dict(),
        }
    }

    _upload_activity(user, activity)
    _send_push_notification(
        user, 
        follower.username + " started following you!",
        'new_follower',
    )


def add_follower(user, follower):
    activity = {
        'type': 'follower',
        'data': {
            'follower': follower.to_dict(),
        }
    }

    _upload_activity(user, activity)
    _send_push_notification(
        user, 
        follower.username + " started following you!",
        'follower',
    )
