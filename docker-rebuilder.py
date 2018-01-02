#!/usr/bin/python3
import time, logging, sys

from lib.globals import DEFAULT_INTERVAL, CONFIGURATION_FILENAME
from lib.configuration import read_configuration, ConfigurationException
from lib.imagewatcher import ImageWatcher

def main(client, configuration):
	watcher = ImageWatcher(client)
	interval = configuration.get("options", {}).get("interval", DEFAULT_INTERVAL)
	
	loop_time = time.time()
	logging.info(watcher.last_seen_images())
	
	while True:
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
		system.exit(1)

