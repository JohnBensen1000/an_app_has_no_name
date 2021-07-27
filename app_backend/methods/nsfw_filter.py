from google.cloud import vision

visionClient = vision.ImageAnnotatorClient()

def check_if_post_is_safe(downloadURL):
	image                  = vision.Image()
	image.source.image_uri = downloadURL
	safe                   = visionClient.safe_search_detection(image=image).safe_search_annotation

	for safeAttribute in [safe.adult, safe.medical, safe.violence]:
		if safeAttribute.value >= 5:
			return False

	return True