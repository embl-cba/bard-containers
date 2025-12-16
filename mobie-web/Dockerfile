FROM jlesage/baseimage-gui:ubuntu-22.04-v4.9.0

ARG DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64" 
ENV PATH=$JAVA_HOME:$PATH


RUN apt-get update -y && \
    apt-get install -y jq \
                       unzip \
                       python3 \
                       python3-pip \
		       python3-tk \
                       python3-requests \
                       build-essential \
                       git \
                       software-properties-common \
                       libxi6 \
                       libxrender1 \
                       libxtst6 \
                       libfreetype6 \
                       fonts-dejavu \
                       fontconfig \
                       nvidia-opencl-dev \
                       ocl-icd-opencl-dev \
                       bzip2 \
                       wget \
                       ca-certificates \
                       curl \
                       firefox \
                       libglu1-mesa-dev \
                       libgl1-mesa-glx \
                       nautilus \
                       xdg-utils \
                       maven \
                       konsole \
                       openjdk-8-jdk && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections 

WORKDIR /tmp
RUN wget https://downloads.imagej.net/fiji/archive/20241226-1317/fiji-linux64.zip && \
    unzip -d /usr/local/ /tmp/fiji-linux64.zip && \
    rm /tmp/fiji-linux64.zip

RUN /usr/local/Fiji.app/ImageJ-linux64 --headless --update add-update-site IJPB-plugins https://sites.imagej.net/IJPB-plugins/ && \
    /usr/local/Fiji.app/ImageJ-linux64 --headless --update add-update-site MoBIE https://sites.imagej.net/MoBIE/ && \
    /usr/local/Fiji.app/ImageJ-linux64 --headless --update add-update-site BigDataProcessor https://sites.imagej.net/BigDataProcessor/ && \
    /usr/local/Fiji.app/ImageJ-linux64 --headless --update add-update-site 3D_ImageJ_Suite https://sites.imagej.net/Tboudier/ && \
    
    /usr/local/Fiji.app/ImageJ-linux64 --ij2 --headless --update update

WORKDIR /usr/local
# Install MoBIE viewer
RUN git clone https://github.com/mobie/mobie-viewer-fiji.git && \ 
   pip install --no-cache-dir pyimagej scyjava requests jpype1==1.4.1

WORKDIR /usr/local/mobie-viewer-fiji


RUN ./install.sh && \
    chmod -R 777 /root/ && \
    chown -R 1000:1000 /root && \
    sed -i 's|\$HOME/.m2|/root/.m2|g' mobie-project mobie-files mobie-table && \
    sed -i '/-Xmx[0-9]*g \\/a \  -XX:ActiveProcessorCount=2 \\' /usr/local/mobie-viewer-fiji/mobie-* 

COPY mobie-ui.py /usr/local/mobie-viewer-fiji/mobie-ui.py

RUN chmod +x /usr/local/mobie-viewer-fiji/mobie-ui.py && \
    sed -i 's|/.docker-instance|/tmp/.docker-instance|g' /etc/cont-init.d/05-container-instance-uuid.sh

RUN apt-get update && \
    apt-get install -y --no-install-recommends websockify novnc && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 5800

COPY startapp.sh /startapp.sh

RUN chmod +x /startapp.sh

ENV APP_NAME="MoBIE Viewer"

ENV KEEP_APP_RUNNING=0

ENV TAKE_CONFIG_OWNERSHIP=1

COPY rc.xml.template /opt/base/etc/openbox/rc.xml.template
WORKDIR /config
