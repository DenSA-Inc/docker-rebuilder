import json
import os
from schema import SchemaError

from .configuration_schema import CONFIGURATION_SCHEMA

class ConfigurationException(Exception):
	pass

def read_configuration(filename):
	if not os.path.exists(filename):
		raise ConfigurationException("File %s does not exist" % filename)
	
	try:
		with open(filename, "r") as file:
			unsafe_config = json.load(file)
	except ValueError as e:
		raise ConfigurationException("Invalid json in %s" % filename) from e
	except Exception as e:
		raise ConfigurationException("Error occurred while reading %s" % filename) from e
	
	try:
		return CONFIGURATION_SCHEMA.validate(unsafe_config)
	except SchemaError as e:
		raise ConfigurationException("Config does not conform to schema") from e

