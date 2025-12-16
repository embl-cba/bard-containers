#!/bin/bash

vglrun -c proxy google-chrome \
  --enable-features=VaapiVideoDecoder \
  --use-gl=egl \
  --enable-gpu-rasterization \
  --enable-zero-copy \
  --ignore-gpu-blocklist \
  --enable-accelerated-video-decode \
  --disable-software-rasterizer \
  --no-sandbox
