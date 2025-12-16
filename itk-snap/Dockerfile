FROM registry.git.embl.org/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8
USER root

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV NVIDIA_DRIVER_CAPABILITIES "all"

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8


RUN apt-get update -y && apt-get install -y bzip2 wget ca-certificates curl firefox \
    && echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get install -y build-essential \
	nautilus \
        xdg-utils \
        wget \
        konsole \
        libatlas-base-dev \
        apt-utils \
        bzip2 \
        git \
        locales \
        cmake \
        unzip &&  apt-get clean && \
        rm -rf /var/lib/apt/lists/* && \
        sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
        locale-gen

RUN  apt-get update -y && apt-get install --no-install-recommends -y \
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
        libxv1 \
        libxtst6 \
        dbus-x11 \
        libxrandr-dev \
        xvfb \
        libopengl0 \
        libgl1-mesa-glx \
        libglu1-mesa \
        qt6-base-dev \
        qt6-base-dev-tools \
        libqt6core6 \
        libqt6gui6 \
        libqt6widgets6 \
        libxcb-cursor0


WORKDIR /tmp
ARG VIRTUALGL_VERSION=3.1
ARG VIRTUALGL_URL="https://sourceforge.net/projects/virtualgl/files"
RUN curl -fsSL -O "${VIRTUALGL_URL}/virtualgl_${VIRTUALGL_VERSION}_amd64.deb" && \
    apt-get update && apt-get install -y --no-install-recommends ./virtualgl_${VIRTUALGL_VERSION}_amd64.deb && \
    rm -f "virtualgl_${VIRTUALGL_VERSION}_amd64.deb" && \
    rm -rf /var/lib/apt/lists/* && \
    chmod u+s /usr/lib/libvglfaker.so && \
    chmod u+s /usr/lib/libdlfaker.so 

COPY itksnap-4.4.0.zip /opt
WORKDIR /opt
RUN unzip /opt/itksnap-4.4.0.zip

LABEL oc.icon="itk.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDIwMDEwOTA0Ly9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy1TVkctMjAwMTA5MDQvRFREL3N2ZzEwLmR0ZCI+CjxzdmcgdmVyc2lvbj0iMS4wIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiB3aWR0aD0iNDAwLjAwMDAwMHB0IiBoZWlnaHQ9IjQwMC4wMDAwMDBwdCIgdmlld0JveD0iMCAwIDQwMC4wMDAwMDAgNDAwLjAwMDAwMCIKIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIG1lZXQiPgoKPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMC4wMDAwMDAsNDAwLjAwMDAwMCkgc2NhbGUoMC4xMDAwMDAsLTAuMTAwMDAwKSIKZmlsbD0iIzAwMDAwMCIgc3Ryb2tlPSJub25lIj4KPHBhdGggZD0iTTE1NjAgMzI3NyBjLTc2IC0yNCAtMTc5IC0xNTggLTE5NSAtMjU0IGwtNyAtNDMgLTQxIDI0IGMtMjMgMTMgLTU2CjI2IC03MiAyOSAtMTcgMyAtNjQgMjEgLTEwNSA0MCAtODYgNDAgLTEwMCA0NCAtMTU1IDUxIC0xNTMgMTkgLTE2MyAxOSAtMjEwCi00IC0yNSAtMTIgLTYxIC0zNiAtNzkgLTU0IC0zMCAtMjggLTM1IC00MCAtNDYgLTExOSBsLTEzIC04NyAyOCAtMzAgYzMzIC0zNQo2MyAtMzggMTQ1IC0xNCAzMCA5IDg2IDE1IDEyMyAxNCA2NSAtMSAxMzcgLTIyIDEzNyAtMzggMCAtNSAxMSAtMTQgMjQgLTIyCjI5IC0xNSAxMjAgLTEyNSAxNTggLTE4OSA1MCAtODcgNTcgLTEwNiA2NSAtMTk2IGw4IC05MCAzOCAtNiBjMjEgLTMgNjEgLTIKOTAgMyA0MiA4IDU3IDcgNzkgLTcgMjcgLTE1IDMwIC0xNSA2OSA3IGw0MSAyMyAzOSAtMjMgYzQxIC0yNCA4NyAtMjMgMTE3IDEKMTcgMTQgMjQgNiA2NiAtODAgNTEgLTEwMiA2NSAtMjA1IDQyIC0zMDUgLTIzIC05NyAtNDEgLTE0MyAtODAgLTIwMyAtMTggLTI3Ci00OCAtNzYgLTY3IC0xMDggLTM4IC02NiAtMTcxIC0xOTMgLTIzNCAtMjI0IC0yMiAtMTEgLTY4IC0yNiAtMTAyIC0zMyAtNDMKLTkgLTY5IC0yMSAtODggLTM5IC0yNCAtMjYgLTI0IC0yOCAtOCAtNDMgMjIgLTE5IDgyIC0zNiAxODggLTUzIDQ0IC03IDk3Ci0yMSAxMTcgLTI5IDIxIC05IDQ2IC0xNiA1NyAtMTYgMTAgMCA2MSAtMjAgMTEzIC00NSA1MSAtMjUgMTEwIC00OCAxMzIgLTUwCjIxIC0zIDUxIC0xNCA2NyAtMjYgMTYgLTExIDczIC00MSAxMjcgLTY2IDUzIC0yNSAxMTYgLTU5IDEzOSAtNzUgMzUgLTI1IDQ4Ci0yOSA3NyAtMjQgMjggNSA0MSAxNiA2MSA1MCAzMSA1MyAzMSA3MCAzIDg4IC0yNyAxNyAtMTM2IDUzIC0xOTMgNjMgLTcyIDEyCi0xNzIgODYgLTIxNyAxNjAgLTEyIDIwIC0xOCA0OSAtMTggODkgMCA0OSA1IDY1IDI2IDk0IDE3IDIyIDMyIDYwIDQwIDEwNCA3CjM5IDMyIDEwNyA1NCAxNTIgMzIgNjUgNDQgMTAzIDU1IDE4MiAyNCAxNjUgMjAgMjExIC0yNSAzNDcgLTIzIDY1IC0zOSAxMjEKLTM3IDEyMyA3IDggMTg3IC0xNzcgMjE0IC0yMTkgMTQgLTIzIDM0IC00OCA0NCAtNTUgMTAgLTcgMjcgLTMyIDM3IC01NiAzNwotODIgMTE4IC0xOTIgMjA4IC0yODEgOTcgLTk2IDIyNCAtMjQ4IDIyNCAtMjY4IDAgLTcgMjYgLTQzIDU3IC04MiBsNTcgLTcwIDYKLTEyMiBjNSAtMTE3IDYgLTEyMyAzMyAtMTUxIDMzIC0zNCAyMDggLTExNSAyMzAgLTEwNiA5IDMgMjMgMjEgMzEgMzkgMTQgMjkKMTUgNTcgOCAyMDIgLTggMTYxIC0xMCAxNzMgLTUxIDI5MyAtNTIgMTUwIC03NiAyMTEgLTE0NiAzNTUgLTMwIDYxIC02NSAxNDQKLTc5IDE4NSAtMTQgNDEgLTM3IDk3IC01MSAxMjQgLTE0IDI3IC0yNSA1NyAtMjUgNjUgMCA5IC02IDI2IC0xNCAzNyAtOCAxMQotMjMgNDEgLTMyIDY1IC0zOCA5OSAtMTQ5IDI0MyAtMjI0IDI5MyAtMTQgOSAtNjQgNTMgLTExMSA5OSAtNDcgNDUgLTk5IDkxCi0xMTYgMTAyIC02NSA0MiAtMTE3IDgyIC0xODUgMTQzIC0zOCAzNCAtNzQgNjIgLTc5IDYyIC0xNSAwIC0xMDggNzggLTE1OAoxMzIgLTQ4IDUyIC0xNjYgMTM3IC0yMjYgMTYyIC00MiAxOCAtMTMzIDE5IC0xODUgM3oiLz4KPC9nPgo8L3N2Zz4K"
LABEL oc.keyword="ITK-SNAP"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.ubuntu.22.04"
LABEL oc.name="ITK-SNAP"
LABEL oc.launch="ITK-SNAP.konsole"
LABEL oc.args="--name ITK-SNAP --hold -e vglrun -c proxy /opt/itksnap-4.4.0/bin/itksnap"
LABEL oc.displayname="itk-SNAP"
LABEL oc.path="/usr/bin/konsole"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.showinview=dock
LABEL oc.acl="{\"permit\":[\"all\"]}"

RUN  if [ -d /usr/share/icons ];   then cd /usr/share/icons;    /composer/safelinks.sh; fi \
     &&  if [ -d /usr/share/pixmaps ]; then cd /usr/share/pixmaps;  /composer/safelinks.sh; fi 

ENV APPNAME "ITK-SNAP"
ENV APPBIN "/usr/bin/konsole"
ENV APP "/usr/bin/konsole"
ENV ARGS="--name ITK-SNAP --hold -e vglrun -c proxy /opt/itksnap-4.4.0/bin/itksnap"

RUN mkdir -p /run/user \
    && chmod 777 /run/user

USER root
RUN mkdir -p /etc/localaccount \
    && for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

CMD ["sh", "-c","mkdir -p ~/tmp && /composer/appli-docker-entrypoint.sh " ]


