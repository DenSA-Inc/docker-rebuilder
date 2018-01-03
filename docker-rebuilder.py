#!/usr/bin/python3
import time, logging, sys

from lib.globals import DEFAULT_INTERVAL, CONFIGURATION_FILENAME
from lib.configuration import read_configuration, ConfigurationException
from lib.imagewatcher import ImageWatcher
from lib.rebuilder import DockerRebuilder

def main(client, configuration):
	watcher = ImageWatcher(client)
	rebuilders = [DockerRebuilder(name, client, configuration["builds"][name]) for name in configuration["builds"]]
	
	watched_images = set()
	for reb in rebuilders: watched_images.update(reb.get_dependencies())
	
	interval = configuration.get("options", {}).get("interval", DEFAULT_INTERVAL)
	
	loop_time = time.time()
	logging.debug("Starting with those images in the local registry:", watcher.last_seen_images())
	logging.info("Loaded %i builds" % len(rebuilders))
	while True:
		watcher.pull(watched_images)
		changed = watcher.find_changed_images()
		
		for reb in rebuilders:
			reb.check_rebuild(changed)
		
		time.sleep(max(0, loop_time + interval - time.time()))
		loop_time += interval

if __name__ == "__main__":
	import docker
	
	logging.basicConfig(format = "%(asctime)s - %(levelname)s: %(message)s", level = logging.INFO)
	logging.info("Starting up")
	
	try:
		configuration = read_configuration(CONFIGURATION_FILENAME)
	except ConfigurationException as e:
		logging.error("Could not read configuration", e)
		sys.exit(1)
	except Exception as e:
		logging.error("My my, how did this happen?", e)
		sys.exit(1)
	
	if "options" in configuration:
		options = configuration["options"]
		
		if options["log-level"]:
			logging.root.setLevel(options["log-level"])
		if options["log-format"]:
			logging.root.handlers[0].setFormatter(logging.Formatter(options["log-format"]))
	
	docker_client = docker.from_env()
	
	try:
		main(docker_client, configuration)
	except KeyboardInterrupt:
		pass
	except Exception as e:
		logging.error("Looks like we went out with a bang", e)
		sys.exit(1)

