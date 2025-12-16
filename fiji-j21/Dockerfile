FROM registry.git.embl.org/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8

USER root

ARG DEBIAN_FRONTEND=noninteractive
ENV CONDA_BIN_PATH="/opt/conda/bin"
ENV PATH $CONDA_BIN_PATH:$PATH
RUN apt-get update -y && \
    apt-get install -y jq unzip wget build-essential git software-properties-common libxi6 libxrender1 libxtst6 libfreetype6 fonts-dejavu fontconfig nvidia-opencl-dev ocl-icd-opencl-dev && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN wget -O /tmp/fiji-linux64.zip https://downloads.imagej.net/fiji/latest/fiji-latest-linux64-jdk.zip && unzip /tmp/fiji-linux64.zip -d /usr/local/

RUN /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site ImageScience  https://sites.imagej.net/ImageScience/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site IJPB-plugins https://sites.imagej.net/IJPB-plugins/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site MoBIE https://sites.imagej.net/MoBIE/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site clijx-assistant-extensions https://sites.imagej.net/clijx-assistant-extensions/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site clijx-assistant https://sites.imagej.net/clijx-assistant/ &&\
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site CLIJ2 https://sites.imagej.net/clij2/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site CLIJ https://sites.imagej.net/clij/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site BigDataProcessor https://sites.imagej.net/BigDataProcessor/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site BoneJ https://sites.imagej.net/BoneJ/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site BIG-EPFL https://sites.imagej.net/BIG-EPFL/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site 3DImageJSuite https://sites.imagej.net/Tboudier/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site MultiStackReg https://sites.imagej.net/MultiStackReg/ && \
#    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site ilastik https://sites.imagej.net/Ilastik/ && \

    /usr/local/Fiji/fiji-linux-x64 --headless --update update

#miniforge
#WORKDIR /tmp
#RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
#    && bash Miniforge3-Linux-x86_64.sh -b -p /opt/conda \
#    && rm -f Miniforge3-Linux-x86_64.sh 


#ilastik
#ENV NUMBA_CACHE_DIR=/tmp/numba_cache
#ENV QT_XCB_NO_MITSHM=1
#ENV BIOIMAGEIO_CACHE_PATH="/tmp/$CURRENT_USER/pybio_cache"
#ENV CURRENT_USER=`whoami`
RUN apt-get update -y && apt-get install -y bzip2 wget ca-certificates curl firefox build-essential libglu1-mesa-dev libgl1-mesa-glx nautilus xdg-utils wget konsole

WORKDIR /opt
  
#RUN wget https://files.ilastik.org/ilastik-1.4.1b20-gpu-Linux.tar.bz2 && \
#    tar xjf ilastik-1.*-Linux.tar.bz2 && \
#    rm -f ilastik-1.*-Linux.tar.bz2

#extra fiji plugin
WORKDIR /usr/local/Fiji/plugins
RUN wget https://imagescience.org/meijering/software/download/FeatureJ_.jar && \
    wget https://imagescience.org/meijering/software/download/imagescience.jar


RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

#set ram, threads
COPY jvm.toml /usr/local/Fiji/config/jaunch/jvm.toml

LABEL oc.icon="fiji_icon.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiICAKICAgeG1sbnM6aW5rc2NhcGU9Imh0dHA6Ly93d3cuaW5rc2NhcGUub3JnL25hbWVzcGFjZXMvaW5rc2NhcGUiCiAgIHdpZHRoPSIxMzIiIGhlaWdodD0iMTMyLjE1MDI0Ij4KICA8ZGVmcz4KICAgIDxmaWx0ZXIKICAgICAgIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiIKICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgIGlkPSJmaWx0ZXI0MzIzNC04Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyCiAgICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgICAgc3RkRGV2aWF0aW9uPSIxNS45NTM1MDQiCiAgICAgICAgIGlkPSJmZUdhdXNzaWFuQmx1cjQzMjM2LTYiIC8+CiAgICA8L2ZpbHRlcj4KICAgIDxwYXRoIGlkPSJNYWluIgogICAgICAgZD0ibSA0OTUuNjQxNDQsMTQ0Ni4yNSA1NS44NTg1NiwwIC0wLjY0NjQ1LDI4NC45NTUyIC0xNjkuMDM1MjcsMCAwLC01Ni44NjE0IDExMy44MjMxNiwtMC4wOTQgeiBtIDExMy44NTg1NiwwIDU2LDAgLTAuNjQ2NDUsMTcwLjk1NTIgLTU1LDAgeiBtIC0yMjgsMCA1NiwwIC0wLjY0NjQ1LDE3MC45NTUyIC01NSwwIHogbSAtNTcuOTk4NjUsMjgzLjk0ODQgLTU2LjU2ODU0LDAuNzA3MSAwLjcwNzExLC0zOTguODA4MyAzOTcuMzYwMDgsMC43Nzc4IDAsNTYuNSAtMzQwLjYxNDc2LC0wLjE3ODkgeiIvPgogIDwvZGVmcz4KICA8bWV0YWRhdGE+CiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ+aW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlIHJkZjpyZXNvdXJjZT0iaHR0cDovL3B1cmwub3JnL2RjL2RjbWl0eXBlL1N0aWxsSW1hZ2UiIC8+CiAgICAgICAgPGRjOnRpdGxlPjwvZGM6dGl0bGU+CiAgICAgIDwvY2M6V29yaz4KICAgIDwvcmRmOlJERj4KICA8L21ldGFkYXRhPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02My41MTk4MiwtMzU5LjQzMzY4KXNjYWxlKDAuMjc3ODEwNTEsMC4yNzc4MTA1MSkiPgogICAgPHVzZSB4bGluazpocmVmPSIjTWFpbiIgc3R5bGU9ImZpbGw6IzAwMDAwMDtmaWx0ZXI6dXJsKCNmaWx0ZXI0MzIzNC04KSIvPgogICAgPHVzZSB4bGluazpocmVmPSIjTWFpbiIgc3R5bGU9ImZpbGw6IzY0YTRlMiIvPgogIDwvZz4KPC9zdmc+"
LABEL oc.keyword="fiji"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.gtk"
LABEL oc.name="fiji-j21"
LABEL oc.launch="fiji-Main.fiji-Main"
LABEL oc.displayname="Fiji (J21)"
LABEL oc.path="/usr/local/Fiji/fiji-linux-x64"
LABEL oc.args="-Djava.io.tmpdir=$HOME/tmp -Dij2.plugin.dirs=/usr/local/Fiji/jars:/usr/local/Fiji/plugins:/home/`whoami`/.plugins"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"
RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done


RUN mkdir -p /etc/localaccount
RUN for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

ENV APPNAME "Fiji (J21)"
ENV APPBIN "/usr/local/Fiji/fiji-linux-x64"
ENV APP "/usr/local/Fiji/fiji-linux-x64"
ENV ARGS="-Djava.io.tmpdir=$HOME/tmp -Dij2.plugin.dirs=/usr/local/Fiji/jars:/usr/local/Fiji/plugins:/home/`whoami`/.plugins"
ENV FIJIPATH="/user/local/Fiji"
ENV PATH=$FIJIPATH:$PATH
ENV TMPDIR=$HOME/tmp

CMD ["sh", "-c","mkdir -p ~/tmp && /composer/appli-docker-entrypoint.sh "]
