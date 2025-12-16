#!/bin/bash

export HOME=/config

export PATH=${PATH}:/usr/local/mobie-viewer-fiji


export MAVEN_OPTS="-Dmaven.repo.local=$HOME/.m2/repository"

# Optional safety: tell Java the user.home, too
export JAVA_TOOL_OPTIONS="-Duser.home=$HOME"

/usr/local/mobie-viewer-fiji/mobie-ui.py
