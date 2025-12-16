FROM registry.git.embl.org/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8
USER root

ARG DEBIAN_FRONTEND=noninteractive
ENV CONDA_BIN_PATH="/opt/miniconda3/bin"
ENV PATH $CONDA_BIN_PATH:$PATH
RUN apt-get update -y && \
    apt-get install -y jq unzip wget build-essential git software-properties-common libxi6 libxrender1 libxtst6 libfreetype6 fonts-dejavu fontconfig nvidia-opencl-dev ocl-icd-opencl-dev  libxcb-cursor-dev libxcb-xinerama0 libxcb-cursor0 bzip2 wget ca-certificates curl firefox build-essential libglu1-mesa-dev libgl1-mesa-glx nautilus xdg-utils wget konsole && \
    echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN wget -O /tmp/fiji-linux64.zip https://downloads.imagej.net/fiji/latest/fiji-latest-linux64-jdk.zip && unzip /tmp/fiji-linux64.zip -d /usr/local/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site ImageScience  https://sites.imagej.net/ImageScience/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site IJPB-plugins https://sites.imagej.net/IJPB-plugins/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site MoBIE https://sites.imagej.net/MoBIE/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site BigDataProcessor https://sites.imagej.net/BigDataProcessor/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site BIG-EPFL https://sites.imagej.net/BIG-EPFL/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site 3DImageJSuite https://sites.imagej.net/Tboudier/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Weka https://sites.imagej.net/TrackMate-Weka/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMateCSVImporter https://sites.imagej.net/TrackMateCSVImporter/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-StarDist https://sites.imagej.net/TrackMate-StarDist/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Pairing https://sites.imagej.net/TrackMate-Pairing/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-MorphoLibJ https://sites.imagej.net/TrackMate-MorphoLibJ/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Lacss https://sites.imagej.net/TrackMate-Lacss/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Kymograph https://sites.imagej.net/TrackMate-Kymograph/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Ilastik https://sites.imagej.net/TrackMate-Ilastik/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Helper https://sites.imagej.net/TrackMate-Helper/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-ExTrack https://sites.imagej.net/TrackMate-ExTrack/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-Cellpose https://sites.imagej.net/TrackMate-Cellpose/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site TrackMate-v8-preview https://sites.imagej.net/TrackMate-Dev-Omnipose/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site Mastodon https://sites.imagej.net/Mastodon-jungle/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site Mastodon-Benchmark https://sites.imagej.net/Mastodon-Benchmark/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site Mastodon-DeepLineage https://sites.imagej.net/Mastodon-DeepLineage/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site Mastodon-Tomancak https://sites.imagej.net/Mastodon-Tomancak/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site CellTrackingChallenge https://sites.imagej.net/Ulman/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update add-update-site MultiStackReg https://sites.imagej.net/MultiStackReg/ && \
    /usr/local/Fiji/fiji-linux-x64 --headless --update update

#miniforge
WORKDIR /tmp
RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
    && bash Miniforge3-Linux-x86_64.sh -b -p /opt/miniconda3 \
    && rm -f Miniforge3-Linux-x86_64.sh 

#omnipose
RUN mamba create -y --name omnipose python==3.9.18 -c conda-forge \
    && mamba run --name omnipose python -m pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --extra-index-url https://download.pytorch.org/whl/cu118 \
    && mamba run --name omnipose python -m pip install pyqt6==6.9.1 pyqt6-qt6==6.9.1 pyqtgraph darkdetect qtpy pygments superqt urllib3 pyasn1 protobuf idna google-crc32c charset_normalizer certifi cachetools rsa requests pyasn1-modules proto-plus googleapis-common-protos google-resumable-media google-auth google-api-core google-cloud-core google-cloud-storage \
    && mamba run --name omnipose python -m pip install natsort scipy==1.11.4 fastremap==1.12.2 omnipose==1.0.6 omnipose-theme numpy==1.26.4

#trackastra
RUN mamba create -y --name trackastra python=3.10 -c conda-forge \
    && mamba install -n trackastra -c conda-forge -c gurobi -c funkelab ilpy \
    && mamba run --name trackastra python -m pip install "trackastra[ilp]" \
    && mkdir /opt/miniconda3/envs/trackastra/lib/python3.10/site-packages/trackastra/.models \
    && chmod 0777 /opt/miniconda3/envs/trackastra/lib/python3.10/site-packages/trackastra/.models

#cellpose v3.1.1.2
RUN mamba create -y --name cellpose3 python=3.10 -c conda-forge \
    && mamba run --name cellpose3 python -m pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --extra-index-url https://download.pytorch.org/whl/cu118 \
    && mamba run --name cellpose3 python -m pip install pyqt6==6.9.1 pyqt6-qt6==6.9.1 \
    && mamba run --name cellpose3 python -m pip install "cellpose[gui]==3.1.1.2" numpy==1.26.3

#cellpose4
RUN mamba create -y --name cellpose4 python=3.10 -c conda-forge \
    && mamba run --name cellpose4 python -m pip install torch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 --extra-index-url https://download.pytorch.org/whl/cu118 \
    && mamba run --name cellpose4 python -m pip install pyqt6==6.9.1 pyqt6-qt6==6.9.1 \
    && mamba run --name cellpose4 python -m pip uninstall PyQt5 \
    && mamba run --name cellpose4 python -m pip install "cellpose[gui]==4.0.6"

LABEL oc.icon="fiji_icon.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiICAKICAgeG1sbnM6aW5rc2NhcGU9Imh0dHA6Ly93d3cuaW5rc2NhcGUub3JnL25hbWVzcGFjZXMvaW5rc2NhcGUiCiAgIHdpZHRoPSIxMzIiIGhlaWdodD0iMTMyLjE1MDI0Ij4KICA8ZGVmcz4KICAgIDxmaWx0ZXIKICAgICAgIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiIKICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgIGlkPSJmaWx0ZXI0MzIzNC04Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyCiAgICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgICAgc3RkRGV2aWF0aW9uPSIxNS45NTM1MDQiCiAgICAgICAgIGlkPSJmZUdhdXNzaWFuQmx1cjQzMjM2LTYiIC8+CiAgICA8L2ZpbHRlcj4KICAgIDxwYXRoIGlkPSJNYWluIgogICAgICAgZD0ibSA0OTUuNjQxNDQsMTQ0Ni4yNSA1NS44NTg1NiwwIC0wLjY0NjQ1LDI4NC45NTUyIC0xNjkuMDM1MjcsMCAwLC01Ni44NjE0IDExMy44MjMxNiwtMC4wOTQgeiBtIDExMy44NTg1NiwwIDU2LDAgLTAuNjQ2NDUsMTcwLjk1NTIgLTU1LDAgeiBtIC0yMjgsMCA1NiwwIC0wLjY0NjQ1LDE3MC45NTUyIC01NSwwIHogbSAtNTcuOTk4NjUsMjgzLjk0ODQgLTU2LjU2ODU0LDAuNzA3MSAwLjcwNzExLC0zOTguODA4MyAzOTcuMzYwMDgsMC43Nzc4IDAsNTYuNSAtMzQwLjYxNDc2LC0wLjE3ODkgeiIvPgogIDwvZGVmcz4KICA8bWV0YWRhdGE+CiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ+aW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlIHJkZjpyZXNvdXJjZT0iaHR0cDovL3B1cmwub3JnL2RjL2RjbWl0eXBlL1N0aWxsSW1hZ2UiIC8+CiAgICAgICAgPGRjOnRpdGxlPjwvZGM6dGl0bGU+CiAgICAgIDwvY2M6V29yaz4KICAgIDwvcmRmOlJERj4KICA8L21ldGFkYXRhPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02My41MTk4MiwtMzU5LjQzMzY4KXNjYWxlKDAuMjc3ODEwNTEsMC4yNzc4MTA1MSkiPgogICAgPHVzZSB4bGluazpocmVmPSIjTWFpbiIgc3R5bGU9ImZpbGw6IzAwMDAwMDtmaWx0ZXI6dXJsKCNmaWx0ZXI0MzIzNC04KSIvPgogICAgPHVzZSB4bGluazpocmVmPSIjTWFpbiIgc3R5bGU9ImZpbGw6IzY0YTRlMiIvPgogIDwvZz4KPC9zdmc+"
LABEL oc.keyword="fiji"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.gtk"
LABEL oc.name="fiji"
LABEL oc.launch="sun-awt-X11-XFramePeer.net-imagej-launcher-ClassLauncher"
LABEL oc.displayname="Fiji"
LABEL oc.path="/usr/local/Fiji/fiji-linux-x64"
LABEL oc.args="-Djava.io.tmpdir=$HOME/tmp -Dij2.plugin.dirs=/usr/local/Fiji/jars:/usr/local/Fiji/plugins:/home/`whoami`/.plugins"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"
Label oc.showinview=dock

RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done && \
    mkdir -p /etc/localaccount && \
    for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

ENV APPNAME "Fiji"
ENV APPBIN "/usr/local/Fiji/fiji-linux-x64"
ENV APP "/usr/local/Fiji/fiji-linux-x64"
ENV ARGS="-Djava.io.tmpdir=$HOME/tmp -Dij2.plugin.dirs=/usr/local/Fiji/jars:/usr/local/Fiji/plugins:/home/`whoami`/.plugins"
ENV FIJIPATH="/user/local/Fiji"
ENV PATH=$FIJIPATH:$PATH
ENV TMPDIR=$HOME/tmp

CMD ["sh", "-c","mkdir -p $HOME/tmp && /composer/appli-docker-entrypoint.sh"]
