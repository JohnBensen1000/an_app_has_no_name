import datetime
import json

from django.db import models
from django.utils import timezone

class Preferences(models.Model):
	'''
		Contains a value between 0 and 1 for each relevant type of content. This model is used to
		keep track of what type of content a user is interested in and what types of content a post
		could be labeled as. The property "list" is used to treat the ContentPreferences attributes
		as a list. 
	'''
	male   = models.FloatField(default=.1)
	female = models.FloatField(default=.1)
	other  = models.FloatField(default=.1)

	y0_12  = models.FloatField(default=.1)
	y13_18 = models.FloatField(default=.1)
	y19_24 = models.FloatField(default=.1)
	y25_29 = models.FloatField(default=.1)
	y30_34 = models.FloatField(default=.1)
	y35_39 = models.FloatField(default=.1)
	y40_49 = models.FloatField(default=.1)
	y50_59 = models.FloatField(default=.1)
	y60_up = models.FloatField(default=.1)

	sports    = models.FloatField(default=.1)
	dance     = models.FloatField(default=.1)
	comedy    = models.FloatField(default=.1)
	skits     = models.FloatField(default=.1)
	lifestyle = models.FloatField(default=.1)
	art       = models.FloatField(default=.1)
	selfHelp  = models.FloatField(default=.1)

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
			'uid':      self.uid,
			'userID':   self.userID,
			'username': self.username
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

class ChatMember(models.Model):
	'''
		Has two fields: chatID and member. chatID keeps track of where in Firestore a chat is stored. 
		member is a ForeignKey to a UserProfile. This model is used to keep track of which chats each
		user is currently in. (Could be group chat or direct message). isOwner is True if member is the
		owner of the chat, false otherwise (always False for direct messages).
	'''
	isOwner = models.BooleanField()
	chatID  = models.CharField(max_length=50)
	member  = models.ForeignKey(User, on_delete=models.CASCADE)

class Post(models.Model):
	'''
		Contains data about an individual post. Also contains a many to many field that keeps track of
		the users that have watched this Post in their recommendations or following feeds. 
	'''
	postID      = models.FloatField(primary_key=True)
	isPrivate   = models.BooleanField(default=False)
	isImage     = models.BooleanField()
	timeCreated = models.DateTimeField(default=timezone.now()) 
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