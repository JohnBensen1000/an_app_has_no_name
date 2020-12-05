from django.db import models
from demographics.models import Demographics

# Create your models here.
class VideoProfile(models.Model):
	private = models.BooleanField(default=False)

	demographics = models.OneToOneField(
		Demographics,
		on_delete=models.CASCADE,
	)

