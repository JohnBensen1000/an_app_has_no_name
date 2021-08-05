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

def _send_push_notification(user, notification):
    if user.deviceToken != None and user.deviceToken != '':
        message = messaging.Message(
            notification = messaging.Notification(
                title = notification
            ),
            data = {
                'newActivity': 'True'
            }, 
            token=user.deviceToken
        )

        messaging.send(message)


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
    _send_push_notification(user, user.username + "commented on your post!")

def add_new_follower(user, follower):
    activity = {
        'type': 'new_follower',
        'data': {
            'follower': follower.to_dict(),
        }
    }

    _upload_activity(user, activity)
    _send_push_notification(user, user.username + "started following you!")


def add_follower(user, follower):
    activity = {
        'type': 'follower',
        'data': {
            'follower': follower.to_dict(),
        }
    }

    _upload_activity(user, activity)
    _send_push_notification(user, user.username + "started following you!")
