from django.db import models

# Create your models here.
class Demographics(models.Model):
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
	selfhelp  = models.FloatField(default=.1)

	def get_list(self):
		return list(self.__dict__.values())[2: ]

	def set_list(self, newDemo):
		nonFloatOffset = 0

		for i, (key, value) in enumerate(self.__dict__.items()):
			if isinstance(value, float):
				self.__dict__[key] = newDemo[i - nonFloatOffset]
			else:
				nonFloatOffset += 1

		self.save()


