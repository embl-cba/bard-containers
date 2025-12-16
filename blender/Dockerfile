FROM registry.git.embl.org/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-12-3

ARG DEBIAN_FRONTEND=noninteractive
ENV BLENDER_USER_SCRIPTS=/opt/blender-addons/scripts/
ENV BLENDER_USER_CONFIG=/opt/blender-addons/config/
ENV NVIDIA_DRIVER_CAPABILITIES all
ENV VGL_DISPLAY egl0
ENV VGL_COMPRESS proxy
 
RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    git \
    unzip \
    libx11-6 \
    libxi6 \
    libgl1 \
    libxxf86vm1 \
    libxrandr2 \
    libxcursor1 \
    libxinerama1 \
    libglib2.0-0 \
    libxkbcommon0 \
    libxrender1 \
    libsm6 \
    ca-certificates \
    xz-utils \
    libxkbcommon0 \
    konsole \
    software-properties-common \
    build-essential \
    curl \
    libglvnd-dev \
    libgl1-mesa-dev \
    libegl1-mesa-dev \
    libgles2-mesa-dev \
    libglu1-mesa-dev \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1 \
    libgles2 \
    libglu1 \
    mesa-utils \
    libxcb1 \
    libxext6 \
    libjack-dev \
    libxv1 \
    libxtst6 \
    dbus-x11 \
    libxrandr-dev \
    xvfb \ 
    && rm -rf /var/lib/apt/lists/*


WORKDIR /tmp
ARG VIRTUALGL_VERSION=3.1
ARG VIRTUALGL_URL="https://sourceforge.net/projects/virtualgl/files"
RUN curl -fsSL -O "${VIRTUALGL_URL}/virtualgl_${VIRTUALGL_VERSION}_amd64.deb" && \
    apt-get update && apt-get install -y --no-install-recommends ./virtualgl_${VIRTUALGL_VERSION}_amd64.deb && \
    rm -f "virtualgl_${VIRTUALGL_VERSION}_amd64.deb" && \
    rm -rf /var/lib/apt/lists/* && \
    chmod u+s /usr/lib/libvglfaker.so && \
    chmod u+s /usr/lib/libdlfaker.so 

WORKDIR /opt/blender
COPY blender-custom.zip /opt/blender

RUN  unzip blender-custom.zip && \
     rm blender-custom.zip && \
     ln -s /opt/blender/bin/blender /usr/local/bin/blender
 

RUN mkdir -p /opt/blender-addons/scripts/addons && mkdir -p /opt/blender-addons/config

WORKDIR /tmp
RUN git clone https://github.com/oanegros/MicroscopyNodes.git && \
    mkdir -p /opt/blender-addons/scripts/addons && \
    mv MicroscopyNodes/microscopynodes /opt/blender-addons/scripts/addons

RUN sed -i '1i\
bl_info = {\n\
    "name": "Microscopy Nodes",\n\
    "author": "oanegros",\n\
    "version": (1, 0),\n\
    "blender": (4, 4, 3),\n\
    "location": "Node Editor",\n\
    "description": "Tools for microscopy image workflows",\n\
    "category": "Node"\n\
}\n\
' /opt/blender-addons/scripts/addons/microscopynodes/__init__.py

RUN /opt/blender/bin/4.5/python/bin/python3.11 -m ensurepip && \
    /opt/blender/bin/4.5/python/bin/python3.11 -m pip install --upgrade pip && \
    /opt/blender/bin/4.5/python/bin/python3.11 -m pip install dask bpy==4.4.0 tifffile==2023.4.12 scikit-image==0.22.0 cmap zarr s3fs


COPY enable_gpu.py /opt/enable_gpu.py

RUN blender --background --factory-startup --python /opt/enable_gpu.py

LABEL oc.icon="blender.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBzdHlsZT0iY2xpcC1ydWxlOmV2ZW5vZGQ7ZmlsbC1ydWxlOmV2ZW5vZGQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1taXRlcmxpbWl0OjIiIHZlcnNpb249IjEuMSIgdmlld0JveD0iMCAwIDE4MSAxNDgiIHhtbDpzcGFjZT0icHJlc2VydmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgICA8dGl0bGU+QmxlbmRlciBsb2dvICh3aXRob3V0IHRleHQpPC90aXRsZT4KICAgIDxnIHRyYW5zZm9ybT0ibWF0cml4KC4yODEgMCAwIC4yODEgLTQxLjggLTQzLjcpIj4KICAgICAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgyMS42IDAgMCAyMS42IC00ODU3IDc2NjUpIj4KICAgICAgICAgICAgPHBhdGggZD0ibTI0My0zMzRjMC4xMDYtMS44OSAxLjAzLTMuNTYgMi40My00Ljc0IDEuMzctMS4xNiAzLjIxLTEuODcgNS4yMy0xLjg3IDIuMDEgMCAzLjg1IDAuNzA5IDUuMjIgMS44NyAxLjQgMS4xOCAyLjMyIDIuODUgMi40MyA0Ljc0IDAuMTA2IDEuOTQtMC42NzUgMy43NS0yLjA0IDUuMDktMS40IDEuMzYtMy4zOCAyLjIyLTUuNjEgMi4yMnMtNC4yMi0wLjg1NC01LjYxLTIuMjJjLTEuMzctMS4zNC0yLjE1LTMuMTQtMi4wNC01LjA4eiIgc3R5bGU9ImZpbGwtcnVsZTpub256ZXJvO2ZpbGw6I2ZmZiIvPgogICAgICAgIDwvZz4KICAgICAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgxMS4xIDAgMCAxMS4xIC0yMjE1IDQxNTMpIj4KICAgICAgICAgICAgPHBhdGggZD0ibTI0My0zMzRjMC4xMDYtMS44OSAxLjAzLTMuNTYgMi40My00Ljc0IDEuMzctMS4xNiAzLjIxLTEuODcgNS4yMy0xLjg3IDIuMDEgMCAzLjg1IDAuNzA5IDUuMjIgMS44NyAxLjQgMS4xOCAyLjMyIDIuODUgMi40MyA0Ljc0IDAuMTA2IDEuOTQtMC42NzUgMy43NS0yLjA0IDUuMDktMS40IDEuMzYtMy4zOCAyLjIyLTUuNjEgMi4yMnMtNC4yMi0wLjg1NC01LjYxLTIuMjJjLTEuMzctMS4zNC0yLjE1LTMuMTQtMi4wNC01LjA4eiIgc3R5bGU9ImZpbGwtcnVsZTpub256ZXJvO2ZpbGw6IzI2NTc4NyIvPgogICAgICAgICAgICA8cGF0aCBkPSJtMjMxLTMzMGMwLjAxMyAwLjc0IDAuMjQ5IDIuMTggMC42MDMgMy4zIDAuNzQ0IDIuMzggMi4wMSA0LjU4IDMuNzYgNi41MSAxLjggMS45OSA0LjAyIDMuNTkgNi41OCA0LjczIDIuNjkgMS4xOSA1LjYxIDEuOCA4LjY0IDEuOCAzLjAzLTRlLTMgNS45NS0wLjYyNCA4LjY0LTEuODMgMi41Ni0xLjE1IDQuNzgtMi43NSA2LjU4LTQuNzUgMS43Ni0xLjk1IDMuMDItNC4xNSAzLjc2LTYuNTMgMC4zNzUtMS4yIDAuNjEyLTIuNDIgMC43MDctMy42NCAwLjA5My0xLjIgMC4wNTQtMi40MS0wLjExNy0zLjYyLTAuMzM0LTIuMzUtMS4xNS00LjU2LTIuNC02LjU2LTEuMTQtMS44NS0yLjYyLTMuNDYtNC4zOC00LjgybDRlLTMgLTNlLTMgLTE3LjctMTMuNmMtMC4wMTYtMC4wMTItMC4wMjktMC4wMjUtMC4wNDYtMC4wMzYtMS4xNi0wLjg5Mi0zLjEyLTAuODg5LTQuMzkgNWUtMyAtMS4yOSAwLjkwNC0xLjQ0IDIuNC0wLjI5IDMuMzRsLTVlLTMgNWUtMyA3LjM5IDYuMDEtMjIuNSAwLjAyNGgtMC4wM2MtMS44NiAyZS0zIC0zLjY1IDEuMjItNCAyLjc3LTAuMzY0IDEuNTcgMC45IDIuODggMi44NCAyLjg4bC0zZS0zIDdlLTMgMTEuNC0wLjAyMi0yMC40IDE1LjZjLTAuMDI2IDAuMDE5LTAuMDU0IDAuMDM5LTAuMDc4IDAuMDU4LTEuOTIgMS40Ny0yLjU0IDMuOTItMS4zMyA1LjQ2IDEuMjMgMS41NyAzLjg0IDEuNTggNS43OCA5ZS0zbDExLjEtOS4xcy0wLjE2MiAxLjIzLTAuMTQ5IDEuOTZ6bTI4LjYgNC4xMWMtMi4yOSAyLjMzLTUuNSAzLjY2LTguOTYgMy42Ni0zLjQ3IDZlLTMgLTYuNjgtMS4zLTguOTctMy42My0xLjEyLTEuMTQtMS45NC0yLjQ0LTIuNDUtMy44My0wLjQ5Ny0xLjM3LTAuNjktMi44Mi0wLjU2Mi00LjI4IDAuMTIxLTEuNDMgMC41NDctMi44IDEuMjMtNC4wMyAwLjY2OC0xLjIxIDEuNTktMi4zMSAyLjcyLTMuMjQgMi4yMy0xLjgxIDUuMDYtMi44IDguMDItMi44IDIuOTctNGUtMyA1LjggMC45NjkgOC4wMyAyLjc4IDEuMTMgMC45MjQgMi4wNSAyLjAyIDIuNzIgMy4yMyAwLjY4MyAxLjIzIDEuMTEgMi41OSAxLjIzIDQuMDMgMC4xMjYgMS40Ni0wLjA2NyAyLjkxLTAuNTY0IDQuMjgtMC41MDggMS40LTEuMzMgMi43LTIuNDUgMy44NHoiIHN0eWxlPSJmaWxsLXJ1bGU6bm9uemVybztmaWxsOiNlYTc2MDAiLz4KICAgICAgICA8L2c+CiAgICA8L2c+Cjwvc3ZnPgo="
LABEL oc.keyword="blender"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.gtk"
LABEL oc.name="blender"
LABEL oc.launch="blender.konsole"
LABEL oc.args="--name blender --hold -e vglrun -c proxy /usr/local/bin/blender"
LABEL oc.displayname="Blender"
LABEL oc.path="/usr/bin/konsole"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"
LABEL oc.showinview=dock

RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done


RUN mkdir -p /etc/localaccount
RUN for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

ENV APPNAME "Blender"
ENV APPBIN "/usr/bin/konsole"
ENV APP "/usr/bin/konsole"
ENV ARGS="--name blender --hold -e vglrun -c proxy /usr/local/bin/blender"

CMD ["sh", "-c","mkdir -p ~/tmp && /composer/appli-docker-entrypoint.sh "]
