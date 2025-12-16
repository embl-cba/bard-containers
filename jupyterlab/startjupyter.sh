#!/bin/bash

jupyter-lab --allow-root --NotebookApp.token='' --ServerApp.root_dir=$HOME --NotebookApp.browser='/usr/bin/firefox-esr' &

sleep 2

/usr/bin/firefox-esr --new-tab "localhost:8888"



