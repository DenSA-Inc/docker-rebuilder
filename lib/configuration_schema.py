from schema import *
from os import path

_expand_paths = Use(path.expanduser, path.expandvars)

CONFIGURATION_SCHEMA = Schema({
	Optional("options"): {
		Optional("interval"): And(int, lambda n: n > 0),
		Optional("log-level", default = None): int,
		Optional("log-format", default = None): str
	},
	"builds": {
		Optional(str): {
			"dockerfile": And(str, _expand_paths, path.exists),
			"tag": str,
			# additional images whose change triggers a rebuild
			# e.g. when you want to trigger rebuilds when your builder-image changes
			Optional("additional_images", default = []): [str],
			# those images to not trigger a rebuild when changed, for whatever reason you might want to do this
			Optional("exclude_images", default = []): [str],
			
			# if you want to run the build in another directory then the dockerfile-location
			Optional("build_dir"): And(str, _expand_paths, path.isdir),

#			Optional("max-retries"): And(int, lambda n: n >= 0) # maybe later
		}
	}
})

