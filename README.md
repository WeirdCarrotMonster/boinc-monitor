# boinc-monitor

**boinc-monitor** is a simple web service that allowes checking on you boinc clients

## Installation

**boinc-monitor** was written using Python 3.9, but can probably support earlier versions (3.6+).

### Python dependencies

You can install python dependencies with `pip` or `pipenv`:

```
> # Using pip
> pip install -r requirements.txt

> # Using pipenv
> pipenv install
```

### Building web interface

First of all, grab [yarn](https://yarnpkg.com/). Install requirements and build static files:

```
> yarn --cwd gui install
> yarn --cwd gui build
```

### Configuring listen port and boinc-clients

Configuration is handled by [environs](https://pypi.org/project/environs/). This means that you can either pass
options through environment variables, or define them in your `.env` file in project directory.

Boinc client connection parameters are passed in `CLIENTS` variable, described as `boinc://` URI:

```
# Passing single client connection
CLIENTS=boinc://:TOKEN@10.0.0.100?name=homepc
# Or multiple, comma-separated
CLIENTS=boinc://:TOKEN@10.0.0.100?name=homepc,boinc://:TOKEN@10.0.0.200?name=paragon
```

## Running in Docker

You can use provided Dockerfile and docker-compose.yml to build **boinc-monitor** image and run it with Docker. One day i'll publish
image on Docker Hub :)

## Screenshot

![web gui screenshot](https://raw.githubusercontent.com/WeirdCarrotMonster/boinc-monitor/main/screenshot.png)

## Future plans?

1. Improving web interface
2. Statistics page?

I don't currently see this project as a way to *control* your boinc clients, so starting/stopping jobs and adding projects is probably out of scope.
