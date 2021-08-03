import datetime
import os 
import random

from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete 
from django.dispatch import receiver

from google.cloud import firestore
from google.cloud import storage, firestore

db = firestore.Client()

client = storage.Client(project="entropy-317014")

class Preferences(models.Model):
	'''
		Contains a value between 0 and 1 for each relevant type of content. This model is used to
		keep track of what type of content a user is interested in and what types of content a post
		could be labeled as. The property "list" is used to treat the ContentPreferences attributes
		as a list. 
	'''

	food      = models.FloatField(default=.1)
	nature    = models.FloatField(default=.1)
	travel    = models.FloatField(default=.1)
	music     = models.FloatField(default=.1)
	fitness   = models.FloatField(default=.1)
	art       = models.FloatField(default=.1)
	dance     = models.FloatField(default=.1)
	comedy    = models.FloatField(default=.1)

	@property
	def fields(self):
		return list(self.__dict__.keys())[2: ]

	@property
	def list(self):
		return list(self.__dict__.values())[2: ]

	@list.setter
	def list(self, newContentPreferences):
		nonFloatOffset = 0

		for i, (key, value) in enumerate(self.__dict__.items()):
			if isinstance(value, float):
				self.__dict__[key] = newContentPreferences[i - nonFloatOffset]
			else:
				nonFloatOffset += 1

		self.save()

	def to_dict(self):
		keys   = list(self.__dict__.keys())[2: ]
		values = list(self.__dict__.values())[2: ]

		returnList = []
		for i in range(len(keys)):
			returnList.append({keys[i]: values[i]})

		return {'preferences': returnList}

class Profile(models.Model):
	'''
		A user's profile is stored in google cloud storage, and could be an image or a video. This
		model keeps track of if a user has created a profile, if the profile is an image or video,
		and the location of the profile in google cloud storage. 
	'''
	exists      = models.BooleanField(default=False)
	isImage     = models.BooleanField(default=True)
	downloadURL = models.TextField(default="")
	isFlagged   = models.BooleanField(default=False)

	def to_dict(self):
		if self.isFlagged:
			return {
				'exists':      False,
				'isImage':     self.isImage,
				'downloadURL': "",
			}
		else:
			return {
				'exists':      self.exists,
				'isImage':     self.isImage,
				'downloadURL': self.downloadURL,
			}

class User(models.Model):
	'''
		Keeps track of all relevant information of a user's account. deviceToken stores the the token 
		of the last device that a user signed in on. firebaseID storeds the id of the user's firebase 
		account (used for authentication). A user's "friend" is defined as someone that the user both 
		follows and is followed by. The property, "friends", returns all of the user's followers that 
		follow them back. 
	'''
	userID = models.CharField(max_length=50, unique=True) 
	email  = models.CharField(max_length=50, unique=True) 
	phone  = models.CharField(max_length=15, default="") 
	uid    = models.CharField(max_length=50, unique=True) 
	
	deviceToken = models.TextField(default=None, null=True, blank=True)
	isUpdated   = models.BooleanField(default=True)

	username          = models.CharField(max_length=20, default="")
	preferredLanguage = models.CharField(max_length=20, default="")
	profileColor      = models.CharField(max_length=10, default='1')
	signedIn          = models.BooleanField(default=False)

	preferences = models.OneToOneField(
		Preferences, 
		on_delete=models.CASCADE, 
	)
	profile = models.OneToOneField(
		Profile, 
		on_delete=models.CASCADE,
	)

	@property
	def friends(self):
		pass

	def delete_account(self):
		if self.preferences:
			self.preferences.delete()
		if self.profile:
			self.profile.delete()

		return super(self.__class__, self).delete()

	def to_dict(self):
		return {
			'uid':          self.uid,
			'userID':       self.userID,
			'username':     self.username,
			'profileColor': self.profileColor
		}

class Blocked(models.Model):
	'''
		Keeps track of the fact that a user is currently blocking a creator.
	'''
	user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='is_blocking')
	creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")

class Chat(models.Model):
	'''
		Contains information about an individual chat. The value stored in chatID is the location of
		the chat collection in Firestore. The save method generates a random chatID whenever the Chat
		entity is being created (self.pk is assigned when the Chat entity is finally created). If self.pk
		is already defined, than the save() method updates the field 'lastChatTime' to the current time.
	'''
	chatID          = models.CharField(max_length=50, unique=True)
	chatName        = models.CharField(max_length=50, default="")
	isDirectMessage = models.BooleanField(default=False)
	lastChatTime    = models.DateTimeField(null=True, blank=True, default=None)

	def save(self, *args, **kwargs):
		if self.pk is None:
			self.chatID = str(int(100 * datetime.datetime.now().timestamp()))
			db.collection('CHATS').document(self.chatID).set({
				'chatID': self.chatID
			})
		self.lastChatTime = datetime.datetime.now(tz=timezone.utc)
		
		super(Chat, self).save(*args, **kwargs)

	def to_dict(self):
		return {
			'chatID':          self.chatID,
			'chatname':        self.chatName,
			'isDirectMessage': self.isDirectMessage,
			'members':         [chatMember.member.to_dict() for chatMember in ChatMember.objects.filter(chat=self)]
		}

class ChatMember(models.Model):
	'''
		Stores the many-to-many relationship between users and chats. The boolean field, isOwner, is set
		to true if the member is the owner of the chat. The boolean field, isUpdated, is set to true if 
		chat member has seen all the chat items sent in a chat; false otherwise. 
	'''
	member    = models.ForeignKey(User, on_delete=models.CASCADE)
	chat      = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_members')
	isOwner   = models.BooleanField(default=False)
	isUpdated = models.BooleanField(default=True)

class Post(models.Model):
	'''
		Contains data about an individual post. Also contains a many to many field that keeps track of
		the users that have watched this Post in their recommendations or following feeds. 
	'''
	postID      = models.CharField(max_length=100, primary_key=True)
	timeCreated = models.DateTimeField() 
	downloadURL = models.TextField()
	isPrivate   = models.BooleanField(default=False)
	isImage     = models.BooleanField()
	isFlagged   = models.BooleanField(default=False)
	caption	    = models.TextField(default="")

	preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE)

	creator = models.ForeignKey(
		User, 
		on_delete=models.CASCADE, 
		related_name="created"
	)
	
	def save(self, *args, **kwargs):
		if self.timeCreated == None:
			self.timeCreated = datetime.datetime.now(tz=timezone.utc)
		super(Post, self).save()


	def delete_post(self):
		if self.preferences:
			self.preferences.delete()

		return super(self.__class__, self).delete()

	def to_dict(self):
		return {
			'creator':     self.creator.to_dict(),
			'postID':      str(self.postID),
			'isImage':     self.isImage,
			'downloadURL': self.downloadURL,
			'caption':     self.caption,
		}

class WatchedBy(models.Model):
	'''
		Many to many model that keeps track of which users watched which post. Each entity
		contains a User and a Post, and records the fact that a User has watched a Post.
	'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Reported(models.Model):
	'''
		Keeps track of the fact that a user has reported a post. This is used to prevent
		recommending posts that a user has reported.
	'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Following(models.Model):
	'''
		Keeps track of the fact that one user is a creator. The boolean field newFollower is True if
	 	this user is a new follower. When this entity is deleted, deletes all direct messages between
		the follower and the creator. 
	'''

	follower    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followings")
	creator     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
	newFollower = models.BooleanField(default=True)

	def delete(self):
		followerChats = [chatMember.chat.chatID for chatMember in ChatMember.objects.filter(member=self.follower)]
		creatorChats  = [chatMember.chat.chatID for chatMember in ChatMember.objects.filter(member=self.creator)]

		for chat in Chat.objects.filter(isDirectMessage=True).filter(chatID__in=followerChats).filter(chatID__in=creatorChats):
			chat.delete()

		super(Following, self).delete()

	def to_dict(self):
		return {
			'follower': self.follower.uid,
			'creator': self.creator.uid,
			'newFollower': self.newFollower,
		}