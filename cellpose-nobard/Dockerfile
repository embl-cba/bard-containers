# Base image
FROM abcdesktopio/oc.template.ubuntu.22.04:3.2
# Run apt command silently
ARG DEBIAN_FRONTEND="noninteractive"

# Set LOCALE
ENV LANG en_US.UTF-8 \
    LC_ALL en_US.UTF-8 \
    LANGUAGE en_US:en 

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y -q --no-install-recommends \
            gcc \
            wget \
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

# Install miniforge 
WORKDIR /tmp
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    && bash Miniforge3-Linux-x86_64.sh -b -p /opt/conda \
    && rm -f Miniforge3-Linux-x86_64.sh 

# Setting enviroment variables
ENV NUMBA_CACHE_DIR /tmp
ENV CONDA_BIN_PATH "/opt/conda/bin"
ENV PATH $CONDA_BIN_PATH:$PATH
ENV LD_PRELOAD "/usr/lib/x86_64-linux-gnu/libstdc++.so.6"
ENV LD_LIBRARY_PATH "/usr/local/nvidia/lib:/usr/local/nvidia/lib64"
ENV NVIDIA_DRIVER_CAPABILITIES "compute,utility"

# Install CellPose
ENV QT_DEBUG_PLUGINS=1
ENV QT_PLUGIN_PATH="/opt/conda/envs/cellpose/lib/python3.10/site-packages/PyQt6/Qt6/plugins/platforms"

RUN conda install mamba -n base -c conda-forge

RUN conda create -y --name cellpose python=3.10 -c conda-forge && \
    conda run --name cellpose python -m pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --extra-index-url https://download.pytorch.org/whl/cu118 && \
    conda run --name cellpose python -m pip install pyqt6==6.6.1 pyqt6-qt6==6.6.1 && \
    conda run --name cellpose python -m pip install cellpose[gui] numpy==1.26.3
# End of Installation

ENTRYPOINT ["/opt/conda/envs/cellpose/bin/python3","-m","cellpose" ]

