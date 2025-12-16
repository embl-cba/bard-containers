ARG TAG=3.2
FROM abcdesktopio/oc.template.ubuntu.nvidia.22.04:$TAG
USER root
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES all
ENV PATH="/opt/nextflow:/opt/conda/envs/cellpose/bin:${PATH}"


ENV LANG en_US.UTF-8 \
    LC_ALL en_US.UTF-8 \
    LANGUAGE en_US:en  \
    NUMBA_CACHE_DIR=/tmp
ENV CONDA_BIN_PATH="/opt/conda/bin"
ENV PATH $CONDA_BIN_PATH:$PATH
ENV LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libstdc++.so.6"
ENV LD_LIBRARY_PATH "/usr/local/nvidia/lib:/usr/local/nvidia/lib64"

ENV QT_DEBUG_PLUGINS=1
ENV QT_PLUGIN_PATH="/opt/conda/envs/cellpose/lib/python3.10/site-packages/PyQt6/Qt6/plugins/platforms"



RUN apt-get update -y && apt-get install -y wget konsole openjdk-17-jdk  gcc \
            qtcreator \
            python3-dev \
            python3-pip \
            python3-wheel \
            libblas-dev \
            liblapack-dev \
            libgl1 \
            mesa-utils \
            libxcb-cursor0 \
            libgl1-mesa-glx \
            libxcb-xinerama0 \
            libatlas-base-dev \
            gfortran \
            apt-utils \
            bzip2 \
            ca-certificates \
            curl \
            konsole \
            locales \
            libarchive-dev \
            cmake \
            libxcb-cursor0 \
            libxcb-cursor-dev \
            unzip &&  apt-get clean && \
            rm -rf /var/lib/apt/lists/* && \
            sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
            locale-gen



RUN mkdir /opt/nextflow
WORKDIR /opt/nextflow

RUN curl -s https://get.nextflow.io |bash
RUN chmod 0755 /opt/nextflow/nextflow && \
    mv /opt/nextflow/nextflow /usr/local/bin/


WORKDIR /tmp
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    && bash Miniforge3-Linux-x86_64.sh -b -p /opt/conda \
    && rm -f Miniforge3-Linux-x86_64.sh 


RUN conda create -y --name cellpose python=3.10 monai=1.3.0 -c conda-forge && \
    conda run --name cellpose python -m pip install torch==2.1.1 torchvision==0.16.1 torchaudio==2.1.1 --index-url https://download.pytorch.org/whl/cu121 && \
    conda run --name cellpose python -m pip install pyqt6==6.9.1 pyqt6-qt6==6.9.1 && \
    conda run --name cellpose python -m pip uninstall PyQt5 && \
    conda run --name cellpose python -m pip install cellpose[gui] cupy-cuda12x instanseg-torch[full] 

LABEL oc.icon="nf.svg"
LABEL oc.icondata="PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTIiIGhlaWdodD0iNTEyIiB2aWV3Qm94PSIwIDAgNTEyIDUxMiI+PHBhdGggZmlsbD0iIzU4ZjljOSIgZD0iTTUxMiAxMjkuOTZWMzQuMjU1QzQxNy42MyA1NC43MDcgMzQ2LjM4NyA5Ny44MyAyNTcuNTY0IDE4My4xNDJDMTI1Ljk2IDI5LjMwMyAxNS4yNjQgMjAuNTcyIDAgMjAuMTJ2OTcuMjYyYzYuMzc2Ljc4NyA4Ni44NDggMTIuOTggMTg5LjY2NCAxMzYuNzE3QzEzMi42MzIgMzA3LjE5NyA2Ny43MyAzNDcuNjM5IDAgMzcyLjY0OXYxMDEuNDU3Yzk2LjM0LTI4LjQ2NyAxODAuMDk3LTc5LjU5OSAyNDkuMzU3LTE0Mi4yMjdjNjcuNjY3IDg3LjQ2NyAxNjguNyAxNDEuMzkgMjYyLjY0MyAxNjAuMDAxVjM5MS41ODRjLTU3LjExOC0xNC41MjctMTMwLjc5Ni00OS4yODUtMTk0LjM1NC0xMzAuNTk2QzM4OS4zMDMgMTgxLjg1IDQ0My43IDE0NS45NDYgNTEyIDEyOS45NiIvPjwvc3ZnPg=="
LABEL oc.keyword="konsole,nextflow"
LABEL oc.cat="development"
LABEL oc.desktopfile="org.kde.konsole.desktop"
LABEL oc.launch="nextflow.konsole"
LABEL oc.template="abcdesktopio/oc.template.ubuntu.nvidia"
LABEL oc.name="nextflow"
LABEL oc.displayname="Nextflow"
LABEL oc.path="/usr/bin/konsole"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":false}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"


ENV APPNAME "Nextflow"
ENV APPBIN "/usr/bin/konsole"

ENV APP "/usr/bin/konsole"

LABEL oc.showinview="dock"

RUN mkdir -p /run/user && \
    chmod 777 /run/user



RUN mkdir -p /etc/localaccount && \
 for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done


CMD ["/composer/appli-docker-entrypoint.sh" ]


