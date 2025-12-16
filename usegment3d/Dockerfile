FROM registry.git.embl.de/grp-cbbcs/abcdesktop-apps/base-image:rockylinux8-cuda-11-8

RUN dnf install -y epel-release

ENV NVIDIA_DRIVER_CAPABILITIES all
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:/usr/lib64:/usr/lib
ENV VGL_DISPLAY egl
ENV CONDA_BIN_PATH="/opt/conda/bin"
ENV PATH $CONDA_BIN_PATH:$PATH


RUN dnf install -y \
    libglvnd-devel \
    mesa-libGL \
    mesa-libGLw-devel \
    mesa-libGL-devel \
    mesa-libEGL-devel \
    mesa-libGLU-devel \
    mesa-dri-drivers \
    libglvnd-egl \
    libglvnd-glx \
    libglvnd-gles \
    libglvnd-opengl \
    libglvnd-devel \
    konsole5  \
    libxcb \
    libxcb-devel \
    libXext-devel \
    libXv \
    libXtst \
    dbus-x11 \
    libXrandr-devel \
    xorg-x11-server-Xvfb

WORKDIR /tmp
ARG VIRTUALGL_VERSION=3.1
ARG VIRTUALGL_URL="https://sourceforge.net/projects/virtualgl/files"
RUN curl -fsSL -O "${VIRTUALGL_URL}/VirtualGL-${VIRTUALGL_VERSION}.x86_64.rpm" && \
    dnf -y update && dnf install -y ./VirtualGL-${VIRTUALGL_VERSION}.x86_64.rpm && \
    rm -f "VirtualGL-${VIRTUALGL_VERSION}.x86_64.rpm" && \
    chmod u+s /usr/lib64/libvglfaker.so /usr/lib64/libvglfaker-nodl.so /usr/lib64/libvglfaker-opencl.so /usr/lib64/libdlfaker.so /usr/lib64/libgefaker.so

RUN /opt/VirtualGL/bin/vglserver_config -config +s +f -t

RUN dnf update -y && dnf install -y \
    nv-codec-headers \
    xdg-utils \
    libffi \
    alsa-lib-devel \
    fftw-libs \
    gdk-pixbuf2-devel \
    libgfortran \
    gstreamer1-plugins-base \
    nspr-devel \
    nss-devel \
    openjpeg2 \
    mesa-libOSMesa \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    xcb-util \
    libX11-xcb \
    libXinerama \
    libxkbcommon-x11 \
    qt5-qtsvg-devel \
    git \
    wget \
    tar \
    ocl-icd 


WORKDIR /tmp
WORKDIR /tmp
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    && bash Miniforge3-Linux-x86_64.sh -b -p /opt/conda \
    && rm -f Miniforge3-Linux-x86_64.sh 

RUN conda create -n usegment3d python=3.9 && \
    conda install -n usegment3d -c conda-forge scikit-fmm && \
    /opt/conda/envs/usegment3d/bin/pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --index-url https://download.pytorch.org/whl/cu118 && \
    /opt/conda/envs/usegment3d/bin/pip install u-Segment3D

LABEL oc.icon="usegment.svg"
LABEL oc.icondata=""
LABEL oc.keyword="uSegment3D,imaging"
LABEL oc.cat="development"
LABEL oc.desktopfile="org.kde.konsole.desktop"
LABEL oc.launch="usegment.konsole"
#ENV ARGS="--name usegment --hold -e vglrun -c proxy /opt/conda/envs/usegment3d/bin/usegment3D"
LABEL oc.name="usegment"
LABEL oc.displayname="uSegment3D"
LABEL oc.path="/bin/konsole"
LABEL oc.type=app
LABEL oc.showinview="dock"
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"

RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done && \
    mkdir -p /run/user && \
    chmod 777 /run/user &&\
    mkdir -p /etc/localaccount && \
    for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

ENV APPNAME "usegment"
ENV APPBIN "/bin/konsole"
#LABEL oc.args="--name usegment --hold -e vglrun -c proxy /opt/conda/envs/usegment3d/bin/usegment3D"
ENV APP "/bin/konsole"

CMD [ "/composer/appli-docker-entrypoint.sh" ]
