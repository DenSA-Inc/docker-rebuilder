import logging, docker, os.path

class DockerRebuilder:
	def __init__(self, name, client, build_config):
		self.name = name
		self.client = client
		self.tag = build_config["tag"]
		
		self.dockerfile = build_config["dockerfile"]
		if os.path.isdir(self.dockerfile): # if we get a directory we assume there is a Dockerfile inside it
			self.dockerfile += os.path.sep + "Dockerfile"
			
			if not os.path.exists(self.dockerfile):
				raise ValueError("Found no Dockerfile in supplied directory")
		
		self.build_dir = build_config["build_dir"] or os.path.dirname(self.dockerfile)
		
		self.base_image = self._get_base_image(self.dockerfile)
		self.depends_on = [self.base_image] + [
					self._no_none_tag_parse(img) for img in build_config["additional_images"]
					]
		
		for exclude in build_config["exclude_images"]:
			img = self._no_none_tag_parse(exclude)
			
			if img in self.depends_on:
				self.depends_on.remove(img)
			else:
				logging.warn("Attempted to remove %s:%s from dependencies of %s but it didn't exist. Check your configuration."
					% (img[0], img[1], name))
	
	def _get_base_image(self, filename):
		with open(filename) as file:
			from_lines = [line for line in file.readlines() if line.strip().startswith("FROM" + " ")]
			
			if not from_lines: # this should not happen
				logging.warn("Dockerfile %s does not contain a FROM directive" % filename)
				return None
			
			line = from_lines[-1]
			args = line.strip().split()
			
			if len(args) < 2:
				raise ValueError("Found a FROM-directive without image in %s" % filename)
			
			image = args[1]
			return docker.utils.parse_repository_tag(image)
	
	def _no_none_tag_parse(self, repo):
		parsed = docker.utils.parse_repository_tag(repo)
		
		if parsed[1] is None:
			return (parsed[0], "latest")
		else:
			return parsed
	
	def get_dependencies(self):
		return set(self.depends_on)
	
	def build(self):
		list( # go through the returned generator, otherwise the image won't be built
			self.client.api.build(fileobj = open(self.dockerfile, "rb"), tag = self.tag,
						path = self.build_dir)
		)
		logging.info("Rebuilt %s as %s in the docker image registry" % (self.name, self.tag))
	
	def check_rebuild(self, changed_images):
		if any(img in changed_images for img in self.depends_on):
			self.build()
