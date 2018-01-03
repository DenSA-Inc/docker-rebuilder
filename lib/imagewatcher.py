import logging, docker.utils

from .util import DelayedKeyboardInterrupt as dki

class ImageWatcher:
	def __init__(self, client):
		self.client = client
		self.images = self._image_map()
	
	def _image_map(self):
		imgs = {}
		for img in self.client.api.images():
			if not img["RepoTags"]:
				continue # image is not tagged, there most likely exists a newer image that is tagged
			
			for tag in img["RepoTags"]:
				imgs[tag] = img
		
		return imgs
	
	def last_seen_images(self):
		return tuple(self.images.keys())

	def pull(self, images):
		for (name, tag) in images:
			with dki(): # docker-related operations are made uninterruptable so Ctrl-C does not kill them
				pull_result = self.client.api.pull(name, tag)
				
				if "Image is up to date" not in pull_result: # Todo: parse output instead of doing this
					logging.info("Pulled new version of %s:%s" % (name, tag))
	
	def find_changed_images(self):
		new_images = self._image_map()
		
		changed = set()
		for image_id in new_images:
			if image_id not in self.images:
				changed.add(image_id)
			elif new_images[image_id]["Id"] != self.images[image_id]["Id"]:
				changed.add(image_id)
		
		self.images = new_images
		return set(map(docker.utils.parse_repository_tag, changed))

