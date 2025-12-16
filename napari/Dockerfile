ARG TAG=3.2
FROM abcdesktopio/oc.template.ubuntu.22.04:$TAG

USER root

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Europe/Berlin
ENV QT_XCB_NO_MITSHM=1 
ENV NVIDIA_DRIVER_CAPABILITIES "compute,utility"

RUN apt-get update -y && apt-get install -qqy build-essential 

#RUN apt-get install -qqy wget mesa-utils \
#                         libgl1-mesa-glx \
#                         libglib2.0-0 \
#                         libfontconfig1 \
#                         libxrender1 \
#                         libdbus-1-3 \
#                         libxkbcommon-x11-0 \
#                         libxi6 \
#                         libxcb-icccm4 \
#                         libxcb-image0 \
#                         libxcb-keysyms1 \
#                         libxcb-randr0 \
#                         libxcb-render-util0 \
#                         libxcb-xinerama0 \
#                         libxcb-xinput0 \
#                         libxcb-xfixes0 \
#                         libxcb-shape0 \
#                         fonts-dejavu \
#                         libarchive-dev \
#                         fontconfig

#COPY environment.yaml /tmp
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
            locales \
            libarchive-dev \
            cmake \
            libxcb-cursor0 \
            libxcb-cursor-dev \
            unzip &&  apt-get clean

RUN rm -rf /var/lib/apt/lists/* 


RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen


WORKDIR /tmp
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    && bash Miniforge3-Linux-x86_64.sh -b -p /opt/conda \
    && rm -f Miniforge3-Linux-x86_64.sh 


LABEL oc.icon="napari-logo.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZlcnNpb249IjEuMSIgd2lkdGg9IjEwMjRweCIgaGVpZ2h0PSIxMDI0cHgiIHN0eWxlPSJzaGFwZS1yZW5kZXJpbmc6Z2VvbWV0cmljUHJlY2lzaW9uOyB0ZXh0LXJlbmRlcmluZzpnZW9tZXRyaWNQcmVjaXNpb247IGltYWdlLXJlbmRlcmluZzpvcHRpbWl6ZVF1YWxpdHk7IGZpbGwtcnVsZTpldmVub2RkOyBjbGlwLXJ1bGU6ZXZlbm9kZCIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjM2IzNzQ1IiBkPSJNIDM1NC41LDgxLjUgQyA0NTkuMTY3LDgxLjMzMzMgNTYzLjgzNCw4MS41IDY2OC41LDgyQyA3MDMuOTgzLDgyLjE0MDcgNzM5LjMxNyw4NC40NzQxIDc3NC41LDg5QyA4MDMuMDA0LDkyLjU0MTMgODMwLjAwNCwxMDAuODc1IDg1NS41LDExNEMgODg0LjkyNSwxMzAuNzU4IDkwNS43NTgsMTU0LjkyNSA5MTgsMTg2LjVDIDkzMC44MTMsMjIyLjcwNCA5MzcuODEzLDI2MC4wMzggOTM5LDI5OC41QyA5MzkuOTUyLDMxNi44MjMgOTQwLjYxOSwzMzUuMTU2IDk0MSwzNTMuNUMgOTQxLjY2Nyw0NTguODMzIDk0MS42NjcsNTY0LjE2NyA5NDEsNjY5LjVDIDk0MC45ODMsNzA4LjczOSA5MzcuOTgzLDc0Ny43MzkgOTMyLDc4Ni41QyA5MjYuOTA0LDgyMC4xNTYgOTE0LjIzNyw4NTAuNDkgODk0LDg3Ny41QyA4NzAuMDM3LDkwMy43NCA4NDAuNTM3LDkyMC41NzQgODA1LjUsOTI4QyA3NzguODI4LDkzNC4wNDIgNzUxLjgyOCw5MzcuNzA5IDcyNC41LDkzOUMgNzA1Ljg0NCw5MzkuOTYzIDY4Ny4xNzgsOTQwLjYyOSA2NjguNSw5NDFDIDU2My44MzMsOTQxLjY2NyA0NTkuMTY3LDk0MS42NjcgMzU0LjUsOTQxQyAzMTQuOTI2LDk0MS4wMyAyNzUuNTkzLDkzOC4wMyAyMzYuNSw5MzJDIDE1Ni44NjcsOTIwLjM2MyAxMDkuMDMzLDg3NS4xOTcgOTMsNzk2LjVDIDg3LjE2MTIsNzY2LjExMiA4My44Mjc5LDczNS40NDYgODMsNzA0LjVDIDgxLjkwNzIsNjQwLjE3NCA4MS40MDcyLDU3NS44NCA4MS41LDUxMS41QyA4MS40MDcyLDQ0Ny4xNiA4MS45MDcyLDM4Mi44MjYgODMsMzE4LjVDIDgzLjU3NjQsMjgwLjU1NCA4OC41NzY0LDI0My4yMjEgOTgsMjA2LjVDIDExNS4yODksMTQ3LjU0NSAxNTMuNzg5LDExMC43MTIgMjEzLjUsOTZDIDI0MS40NDYsODkuMjk4MyAyNjkuNzc5LDg1LjI5ODMgMjk4LjUsODRDIDMxNy4zMjgsODMuMjAxOSAzMzUuOTk1LDgyLjM2ODYgMzU0LjUsODEuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjZDFjZGM3IiBkPSJNIDMzNS41LDE3OS41IEMgNDAwLjEwOCwxNzcuODg3IDQ1MC45NDEsMjAzLjIyMSA0ODgsMjU1LjVDIDQ5OS44NDIsMjc0LjM1IDUwOC4xNzUsMjk0LjY4MyA1MTMsMzE2LjVDIDUxOS43ODQsMzMyLjI4NCA1MzEuNjE4LDM0MS43ODQgNTQ4LjUsMzQ1QyA1NjMuNTA1LDM0NSA1NzguNTA1LDM0NC41IDU5My41LDM0My41QyA2NzAuNjg2LDM0NS4wMTcgNzM0LjUxOSwzNzQuNjgzIDc4NSw0MzIuNUMgODQwLjc1OCw1MDIuOTU2IDg1Ni40MjQsNTgxLjYyMyA4MzIsNjY4LjVDIDgwNC4xNjcsNzQ5LjY2NyA3NDkuNjY3LDgwNC4xNjcgNjY4LjUsODMyQyA1NzcuOTE5LDg1Ny4wOTggNDk2LjkxOSw4MzkuNDMxIDQyNS41LDc3OUMgMzk1Ljc0Niw3NTEuMzM2IDM3My41NzksNzE4LjUwMiAzNTksNjgwLjVDIDM1My4wMDEsNjU5LjgzOCAzNDcuMDAxLDYzOS4xNzIgMzQxLDYxOC41QyAzMjMuMjM1LDU2OC43NTIgMjk1LjA2OCw1MjUuOTE5IDI1Ni41LDQ5MEMgMTkwLjk0NSw0NDEuMzQ3IDE2Ny43NzgsMzc3LjE4IDE4NywyOTcuNUMgMjEyLjM3MiwyMjcuNzM4IDI2MS44NzIsMTg4LjQwNSAzMzUuNSwxNzkuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjM2I1YTE4IiBkPSJNIDM0NC41LDE5Ni41IEMgNDAwLjQyNiwxOTcuODcxIDQ0My45MjYsMjIxLjUzNyA0NzUsMjY3LjVDIDQ4NS4xMDUsMjg1LjA0OCA0OTIuNDM4LDMwMy43MTUgNDk3LDMyMy41QyA1MDcuNTQ5LDM0Ny4wMzMgNTI1LjcxNiwzNjAuMiA1NTEuNSwzNjNDIDYzNy41MDMsMzUxLjc3MyA3MTAuMDAzLDM3Ny42MDcgNzY5LDQ0MC41QyA4MjUuNDUyLDUxMC4xOTMgODM5Ljc4NSw1ODcuODYgODEyLDY3My41QyA3ODEuNTU2LDc1MC4yNzggNzI2LjM4OSw3OTkuMTEyIDY0Ni41LDgyMEMgNTU2LjU5NCw4MzcuNTg1IDQ4MC40MjgsODEzLjA4NSA0MTgsNzQ2LjVDIDM5OS41ODUsNzI0LjcxIDM4NS4yNTIsNzAwLjM3NyAzNzUsNjczLjVDIDM2OSw2NTIuODMzIDM2Myw2MzIuMTY3IDM1Nyw2MTEuNUMgMzM1LjEyNCw1NTAuODY4IDI5OC45NTcsNTAwLjcwMiAyNDguNSw0NjFDIDIwMi4xMzksNDE2LjczIDE4Ny4zMDUsMzYzLjU2MyAyMDQsMzAxLjVDIDIyMi44MzksMjQ5LjMyOCAyNTkuMDA2LDIxNS44MjggMzEyLjUsMjAxQyAzMjMuMjA1LDE5OC42ODUgMzMzLjg3MiwxOTcuMTg1IDM0NC41LDE5Ni41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjEiIGZpbGw9IiM5M2NmZmIiIGQ9Ik0gMzQwLjUsMjMxLjUgQyAzOTcuMDg0LDIzMS45NTQgNDM1LjkxOCwyNTguMjg3IDQ1NywzMTAuNUMgNDY4LjQ1MSwzNjQuNDU1IDUwMS42MTgsMzkzLjc4OCA1NTYuNSwzOTguNUMgNjM5LjI1LDM4Ny4xNDggNzA1Ljc1LDQxNC40ODEgNzU2LDQ4MC41QyA3OTQuMyw1MzkuMjM5IDgwMS4zLDYwMS41NzMgNzc3LDY2Ny41QyA3NDkuMjk1LDczMC44NjcgNzAxLjc5NSw3NzAuNyA2MzQuNSw3ODdDIDU1MC4yMzksODAwLjkyNyA0ODIuNDA2LDc3NC4wOTQgNDMxLDcwNi41QyA0MjIuNzE0LDY5NC4yNjUgNDE1LjcxNCw2ODEuMjY1IDQxMCw2NjcuNUMgNDAyLjYyLDY0MS4zMTQgMzk0LjYyLDYxNS4zMTQgMzg2LDU4OS41QyAzNjEuMjA3LDUyNy4zODkgMzIyLjcwNyw0NzUuNTU2IDI3MC41LDQzNEMgMjMxLjg1NywzOTUuNDU1IDIyMi4zNTcsMzUwLjYyMiAyNDIsMjk5LjVDIDI2Mi42MzEsMjU5LjEwNSAyOTUuNDY1LDIzNi40MzggMzQwLjUsMjMxLjUgWiIvPjwvZz4KPC9zdmc+Cg=="
LABEL oc.keyword="napari"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.ubuntu.22.04"
LABEL oc.name="napari"
LABEL oc.launch="napari.napari"
LABEL oc.displayname="Napari(devbio)"
LABEL oc.path="/opt/conda/envs/napari/bin/naparia"
LABEL oc.type=app
LABEL oc.showinview=dock
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"


RUN  if [ -d /usr/share/icons ];   then cd /usr/share/icons;    /composer/safelinks.sh; fi 
RUN  if [ -d /usr/share/pixmaps ]; then cd /usr/share/pixmaps;  /composer/safelinks.sh; fi 

ENV APPNAME "napari"
ENV APPBIN "/opt/conda/envs/napari/bin/naparia"
ENV APP "/opt/conda/envs/napari/bin/naparia"

ENV CONDA_BIN_PATH="/opt/conda/bin"
ENV PATH $CONDA_BIN_PATH:$PATH

RUN conda install mamba -n base -c conda-forge && \
   mamba create --name napari napari=0.4.19 python=3.9 devbio-napari pyqt ocl-icd-system -c conda-forge -c pytorch && \
   /opt/conda/envs/napari/bin/pip install torch==1.13.0+cu117 torchvision==0.14.0+cu117 torchaudio==0.13.0 --extra-index-url https://download.pytorch.org/whl/cu117 


RUN mkdir -p /run/user && \
    chmod 777 /run/user && \
    mkdir -p /etc/localaccount && \
    for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done


CMD ["/composer/appli-docker-entrypoint.sh" ]


