import logging

from .util import DelayedKeyboardInterrupt as dki

class ImageWatcher:
	def __init__(self, client):
		self.client = client
		self.images = self._image_map()
	
	def _image_map(self):
		imgs = {}
		for img in self.client.api.images():
			for tag in img["RepoTags"]:
				imgs[tag] = img
		
		return imgs
	
	def last_seen_images(self):
		return tuple(self.images.keys())

	def pull(self, images):
		for (name, tag) in images:
			with dki():
				self.client.api.pull(name, tag)

