### docker-rebuilder - Rebuild your images as soon as their base-images change

docker-rebuilder was created by the need to update private images. For public images, there is v2tec/watchtower (which does its job 
quite well if I might say so). However, watchtower is not able to rebuild your custom favourite project. 

##### Installation

To run this program you have to have Python 3 and the necessary packages installed. The dependencies can be installed via `sudo pip3 install -r requirements.txt`. Provided you have a working configuration docker-rebuilder should be able to launch.

##### Configuration

For an up-to-date explanation visit `lib/configuration_schema.py`, it contains a semi-readable structure of what is expected from the config-file along with some comments.

The config-file (incidentally named `config.json`) has to contain one json-object describing your docker-builds. One example would be:
```
{
  "builds": {
    "descriptive-name-here, anything goes": {
      "dockerfile": "/path/of/your/dockerfile/YouCanAlsoUseACustomDockerfileName",
      "tag": "TheTagYourImageWillReceive",
    }
  }
}
```

This should suffice for normal builds, if that does not match your needs please note that there are some other build-options. For clarity these are not listed here.

If you want to change logging-options or the interval at which the program checks for changed images, use the "options"-block of the configuration:

```
{
  "options": {
    "log-level": pythons logging-modules log-level,
    "log-format": pythons logging-modules log-format,
    "interval": the interval at which to attempt a rebuild
  },
  "builds": {
    ...
  }
}
```

##### How does it work?

Magic and Voodoo. No, it's easy. Every interval (5 minutes by default) the program pulls every image it needs for your builds. If the program detects changes it will check which of your Dockerfile's are based on the changed images and rebuild them.

**Note:** To detect the base-image of your Dockerfile the program looks for the last FROM-directive, builder-images are ignored.

##### Using with docker

docker-rebuilder is available as docker-container. To allow the container to communicate with docker mount the docker-socket-file as volume in the container.

```
docker run ... -v /var/run/docker.sock:/var/run/docker.sock ... densainc/docker-rebuilder
```

If you want to let docker-rebuilder connect to a docker-server via tcp then please experiment with the environment variables. As of now I've not tried that.

Making the configuration available inside the container does not look good, but it works:

```
docker run ... -v /path/to/your/config-file.json:/app/config.json ... densainc/docker-rebuilder
```

In the last step you have to make the files docker-rebuilder has to work on available in the container. Make sure the paths inside the config.json refer to the paths inside the docker container and not the paths of the host machine. To avoid this problem you should consider mounting your project-files under the exact same path in the container, e.g. `-v /my/project/files:/my/project/files`.

If you followed these advices you should be ready to go, at least it works on my machine :D.

##### Bugs

Yes, there are bugs. What did you expect?

##### Future stuff

 - git integration. Similar to images this program would pull the current branch and rebuild on changes
 - dependencies. If the program rebuilds an image that is used by another build the rebuild should happen automatically
 - multithreading. For now every pull/rebuild happens in serial, depending on what you do parallel might be what you need
 - custom options that will be passed to docker in the config-file
