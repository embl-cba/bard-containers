#!/bin/bash

R -e "shiny::runApp('/opt/ide/app/image-data-explorer/image_data_explorer.R', host = '0.0.0.0', port = 5476)" &

sleep 5 && 

/usr/bin/firefox --new-tab http://127.0.0.1:5476

