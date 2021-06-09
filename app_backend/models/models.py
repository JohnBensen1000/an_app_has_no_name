import datetime
import os 
import random

from django.db import models
from django.utils import timezone

from google.cloud import firestore
from google.cloud import storage, firestore

db = firestore.Client()

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
	sports    = models.FloatField(default=.1)
	dance     = models.FloatField(default=.1)
	comedy    = models.FloatField(default=.1)
	skits     = models.FloatField(default=.1)
	lifestyle = models.FloatField(default=.1)
	selfHelp  = models.FloatField(default=.1)
	outdoors  = models.FloatField(default=.1)
	gaming    = models.FloatField(default=.1)

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

class Profile(models.Model):
	'''
		A user's profile is stored in google cloud storage, and could be an image or a video. This
		model keeps track of if a user has created a profile, if the profile is an image or video,
		and the location of the profile in google cloud storage. 
	'''
	exists      = models.BooleanField(default=False)
	isImage     = models.BooleanField(default=True)
	downloadURL = models.CharField(max_length=50, default="")

	def to_dict(self):
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
	phone  = models.CharField(max_length=15, unique=True) 
	uid    = models.CharField(max_length=15, unique=True) 
	
	deviceToken = models.TextField(default="")

	username          = models.CharField(max_length=20, default="")
	preferredLanguage = models.CharField(max_length=20, default="")
	profileColor      = models.CharField(max_length=10, default='blue')
	signedIn          = models.BooleanField(default=False)

	preferences = models.OneToOneField(
		Preferences, 
		on_delete=models.CASCADE, 
	)
	profile = models.OneToOneField(
		Profile, 
		on_delete=models.CASCADE,
	)

	allRelationships = models.ManyToManyField(
		'self', 
		through='Relationships', 
		symmetrical=False
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

class Relationships(models.Model):
	'''
		Defines a one way relationship between one user and another. RELATION_TYPE keeps track of 
		the type of relation that exists between these two users. 
	'''
	following = 0
	blocked   = 1

	RELATION_TYPE = (
		(following, 'Following'),
		(blocked, 'Blocked'),
	)

	follower    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followings")
	creator     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
	relation    = models.IntegerField(choices=RELATION_TYPE, default=following)
	newFollower = models.BooleanField(default=True)

class Chat(models.Model):
	'''
		Contains information about an individual chat. The value stored in chatID is the location of
		the chat collection in Firestore. The save method generates a random chatID whenever the Chat
		entity is being created (self.pk is assigned when the Chat entity is finally created).
	'''
	chatID          = models.CharField(max_length=50, unique=True)
	chatName        = models.CharField(max_length=50, default="")
	isDirectMessage = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if self.pk is None:
			self.chatID = str(int(100 * datetime.datetime.now().timestamp()))
			db.collection(os.environ["CHAT_COLLECTION_NAME"]).document(self.chatID).set({
				'chatID': self.chatID
			})
		
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
		to true if the member is the owner of the chat. 
	'''
	member  = models.ForeignKey(User, on_delete=models.CASCADE)
	chat    = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_members')
	isOwner = models.BooleanField(default=False)

class Post(models.Model):
	'''
		Contains data about an individual post. Also contains a many to many field that keeps track of
		the users that have watched this Post in their recommendations or following feeds. 
	'''
	postID      = models.CharField(max_length=25, primary_key=True)
	isPrivate   = models.BooleanField(default=False)
	isImage     = models.BooleanField()
	timeCreated = models.DateTimeField(default=timezone.now) 
	downloadURL = models.CharField(max_length=75)

	preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE)

	creator = models.ForeignKey(
		User, 
		on_delete=models.CASCADE, 
		related_name="created"
	)

	watchedBy = models.ManyToManyField(
		User,
		related_name="watched",
	)

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
		}