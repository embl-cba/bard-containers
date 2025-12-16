FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -qqy  \
    build-essential \
    git \
    mesa-utils \
    x11-utils \
    libegl1-mesa \
    libopengl0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libxrender1 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    libxi6 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    jq \
    unzip \
    wget \
    software-properties-common \
    libxi6 \
    libxtst6 \
    libfreetype6 \
    fonts-dejavu \
    fontconfig \
    && apt-get clean

# Install Xpra and dependencies
RUN wget -qO- https://xpra.org/gpg.asc | apt-key add - && \
    echo "deb https://xpra.org/ jammy main" > /etc/apt/sources.list.d/xpra.list && \
    apt-get update

RUN apt-get update && apt-get install -y wget gnupg2 apt-transport-https \
    software-properties-common ca-certificates \
    xpra \
    xvfb \
    xterm \
    sshfs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/opt/conda/lib/:/opt/conda/lib/python3.9/site-packages/nvidia/cudnn/lib

# Install Fiji
RUN wget -O /tmp/fiji-linux64.zip https://downloads.imagej.net/fiji/latest/fiji-latest-linux64-jdk.zip && unzip /tmp/fiji-linux64.zip -d /usr/local/


ENV DISPLAY=:100
ENV XPRA_PORT=9876
ENV XPRA_START="/usr/local/Fiji/fiji-linux-x64"
ENV XPRA_EXIT_WITH_CLIENT="yes"
ENV XPRA_XVFB_SCREEN="1920x1080x24+32"
EXPOSE 9876

CMD echo "Launching Fiji on Xpra. Connect via http://localhost:$XPRA_PORT or $(hostname -i):$XPRA_PORT"; \
    xpra start \
    --bind-tcp=0.0.0.0:$XPRA_PORT \
    --html=on \
    --start="$XPRA_START" \
    --exit-with-client="$XPRA_EXIT_WITH_CLIENT" \
    --daemon=no \
    --xvfb="/usr/bin/Xvfb +extension Composite -screen 0 $XPRA_XVFB_SCREEN -nolisten tcp -noreset" \
    --pulseaudio=no \
    --notifications=no \
    --bell=no \
    $DISPLAY

