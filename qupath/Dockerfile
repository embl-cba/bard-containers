FROM registry.git.embl.org/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
    apt-get install -y unzip wget build-essential git tar software-properties-common ca-certificates libgl1 xz-utils openjfx qt5dxcb-plugin && \
     echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN mkdir -p /opt/qupath && \
    chmod 777 /opt/qupath && \
    cd /opt/qupath/ && \
    wget https://github.com/qupath/qupath/releases/download/v0.6.0/QuPath-v0.6.0-Linux.tar.xz && \
    tar -xvf QuPath-v0.6.0-Linux.tar.xz && \
    rm /opt/qupath/QuPath-v0.6.0-Linux.tar.xz -rf && \
    chmod u+x /opt/qupath/QuPath/bin/QuPath

RUN mkdir -p /opt/qupath/user_dir/extensions && \
    chmod -R 0777 /opt/qupath/user_dir/extensions && \
    cd /opt/qupath/user_dir/extensions && \
    wget https://github.com/qupath/qupath-extension-djl/releases/download/v0.4.0/qupath-extension-djl-0.4.0.jar && \
    wget https://github.com/qupath/qupath-extension-instanseg/releases/download/v0.1.3/qupath-extension-instanseg-0.1.3.jar && \
    wget https://github.com/qupath/qupath-extension-stardist/releases/download/v0.6.0/qupath-extension-stardist-0.6.0.jar && \
    wget https://github.com/qupath/qupath-extension-omero/releases/download/v0.1.0/qupath-extension-omero-0.1.0.jar && \
    wget https://github.com/qupath/qupath-extension-omero/releases/download/v0.1.0/qupath-extension-omero-0.1.0-javadoc.jar && \
    wget https://github.com/ome/openmicroscopy/releases/download/v5.6.15/OMERO.java-5.6.15-ice36.zip && \
    unzip OMERO.java-5.6.15-ice36.zip && \
    rm OMERO.java-5.6.15-ice36.zip && \
    chmod -R 755 /opt/qupath/user_dir/

LABEL oc.icon="qupath.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZlcnNpb249IjEuMSIgd2lkdGg9IjMwcHgiIGhlaWdodD0iMzBweCIgc3R5bGU9InNoYXBlLXJlbmRlcmluZzpnZW9tZXRyaWNQcmVjaXNpb247IHRleHQtcmVuZGVyaW5nOmdlb21ldHJpY1ByZWNpc2lvbjsgaW1hZ2UtcmVuZGVyaW5nOm9wdGltaXplUXVhbGl0eTsgZmlsbC1ydWxlOmV2ZW5vZGQ7IGNsaXAtcnVsZTpldmVub2RkIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjEiIGZpbGw9IiMyZjVlOWUiIGQ9Ik0gMjAuNSwyLjUgQyAxOC44MjEyLDIuMjg1MTkgMTcuODIxMiwyLjk1MTg2IDE3LjUsNC41QyAxNC40NDY3LDQuMTEwNjYgMTEuNzgsNC43NzczMyA5LjUsNi41QyA1Ljg0NTc3LDkuMTQwOTkgNC41MTI0MywxMi44MDc3IDUuNSwxNy41QyA1LjUsMTkuMTY2NyA1LjUsMjAuODMzMyA1LjUsMjIuNUMgNC4xNjY2NywyMC44MzMzIDIuODMzMzMsMTkuMTY2NyAxLjUsMTcuNUMgLTAuMDc1OTM1NCw3LjcwMjQgNC4yNTc0LDIuMDM1NzQgMTQuNSwwLjVDIDE2Ljc5ODYsMC41OTkxNTcgMTguNzk4NiwxLjI2NTgyIDIwLjUsMi41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjEiIGZpbGw9IiMzNzZkYjUiIGQ9Ik0gMjAuNSwyLjUgQyAyMy44NDQ2LDMuNjc5OSAyNi4wMTEzLDYuMDEzMjQgMjcsOS41QyAyNy42OTM2LDEzLjU1NCAyNy41MjY5LDE3LjU1NCAyNi41LDIxLjVDIDI1LjUwODQsMjEuMzI4NCAyNC44NDE3LDIxLjY2MTggMjQuNSwyMi41QyAyMi44MDg5LDIzLjg2MzcgMjEuMTQyMywyNS4xOTcgMTkuNSwyNi41QyAxNS40NjU5LDI2LjQ5NTUgMTEuNDY1OSwyNi4xNjIxIDcuNSwyNS41QyA2LjgzMzMzLDI0LjUgNi4xNjY2NywyMy41IDUuNSwyMi41QyA1LjUsMjAuODMzMyA1LjUsMTkuMTY2NyA1LjUsMTcuNUMgNi40NzI1LDE5LjEzOTIgNy44MDU4NCwyMC40NzI2IDkuNSwyMS41QyAxMC43NzY3LDIyLjg5NzYgMTIuNDQzNCwyMy41NjQzIDE0LjUsMjMuNUMgMTcuMTAxNiwyMy41MzI4IDE5LjEwMTYsMjIuNTMyOCAyMC41LDIwLjVDIDIxLjc4OTksMTkuOTQyMyAyMi42MjMyLDE4Ljk0MjMgMjMsMTcuNUMgMjQuOTYwOCwxMS41ODgzIDIzLjEyNzQsNy41ODgzMSAxNy41LDUuNUMgMTcuNSw1LjE2NjY3IDE3LjUsNC44MzMzMyAxNy41LDQuNUMgMTcuODIxMiwyLjk1MTg2IDE4LjgyMTIsMi4yODUxOSAyMC41LDIuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjYmZjMWM3IiBkPSJNIDE3LjUsNC41IEMgMTcuNSw0LjgzMzMzIDE3LjUsNS4xNjY2NyAxNy41LDUuNUMgMTYuMDI3OCw3LjgwNjg4IDE0LjM2MTEsOS45NzM1NCAxMi41LDEyQyAxMy40MDM0LDE1LjA2NzIgMTQuNTcsMTUuNTY3MiAxNiwxMy41QyAxOC4xOTg3LDEzLjY3OTUgMjAuMzY1NCwxMy42Nzk1IDIyLjUsMTMuNUMgMjAuODI4NywxNS41MDk4IDIwLjE2MiwxNy44NDMxIDIwLjUsMjAuNUMgMTkuMTAxNiwyMi41MzI4IDE3LjEwMTYsMjMuNTMyOCAxNC41LDIzLjVDIDEyLjQ0MzQsMjMuNTY0MyAxMC43NzY3LDIyLjg5NzYgOS41LDIxLjVDIDEwLjA4ODksMTkuNjQ4MSAxMC43NTU2LDE3LjgxNDggMTEuNSwxNkMgOS45Njc5OCwxNS4zMDA1IDguOTY3OTgsMTQuMTMzOCA4LjUsMTIuNUMgMTAuMzkwOSwxMS42ODkzIDExLjcyNDIsMTAuMzU1OSAxMi41LDguNUMgMTEuMjE5Miw4Ljk4MzkzIDEwLjIxOTIsOC4zMTcyNiA5LjUsNi41QyAxMS43OCw0Ljc3NzMzIDE0LjQ0NjcsNC4xMTA2NiAxNy41LDQuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjOGM3MjZjIiBkPSJNIDE3LjUsNS41IEMgMjMuMTI3NCw3LjU4ODMxIDI0Ljk2MDgsMTEuNTg4MyAyMywxNy41QyAyMi42MjMyLDE4Ljk0MjMgMjEuNzg5OSwxOS45NDIzIDIwLjUsMjAuNUMgMjAuMTYyLDE3Ljg0MzEgMjAuODI4NywxNS41MDk4IDIyLjUsMTMuNUMgMjAuMzY1NCwxMy42Nzk1IDE4LjE5ODcsMTMuNjc5NSAxNiwxMy41QyAxNC41NywxNS41NjcyIDEzLjQwMzQsMTUuMDY3MiAxMi41LDEyQyAxNC4zNjExLDkuOTczNTQgMTYuMDI3OCw3LjgwNjg4IDE3LjUsNS41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjEiIGZpbGw9IiM5NDdkNzYiIGQ9Ik0gOS41LDYuNSBDIDEwLjIxOTIsOC4zMTcyNiAxMS4yMTkyLDguOTgzOTMgMTIuNSw4LjVDIDExLjcyNDIsMTAuMzU1OSAxMC4zOTA5LDExLjY4OTMgOC41LDEyLjVDIDguOTY3OTgsMTQuMTMzOCA5Ljk2Nzk4LDE1LjMwMDUgMTEuNSwxNkMgMTAuNzU1NiwxNy44MTQ4IDEwLjA4ODksMTkuNjQ4MSA5LjUsMjEuNUMgNy44MDU4NCwyMC40NzI2IDYuNDcyNSwxOS4xMzkyIDUuNSwxNy41QyA0LjUxMjQzLDEyLjgwNzcgNS44NDU3Nyw5LjE0MDk5IDkuNSw2LjUgWiIvPjwvZz4KPGc+PHBhdGggc3R5bGU9Im9wYWNpdHk6MC4wOTYiIGZpbGw9IiMwNTA4MTIiIGQ9Ik0gMS41LDE3LjUgQyAyLjgzMzMzLDE5LjE2NjcgNC4xNjY2NywyMC44MzMzIDUuNSwyMi41QyA2LjE2NjY3LDIzLjUgNi44MzMzMywyNC41IDcuNSwyNS41QyAzLjYzNDg4LDI0LjI5MzggMS42MzQ4OCwyMS42MjcxIDEuNSwxNy41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjAuMDM5IiBmaWxsPSIjZDVkNWQ1IiBkPSJNIDI0LjUsMjIuNSBDIDI0Ljg0MTcsMjEuNjYxOCAyNS41MDg0LDIxLjMyODQgMjYuNSwyMS41QyAyNy4xNjY3LDIyLjgzMzMgMjguMTY2NywyMy44MzMzIDI5LjUsMjQuNUMgMjkuNSwyNS41IDI5LjUsMjYuNSAyOS41LDI3LjVDIDI5LjE2NjcsMjcuNSAyOC44MzMzLDI3LjUgMjguNSwyNy41QyAyNy45MjAyLDI1LjI1MTIgMjYuNTg2OSwyMy41ODQ2IDI0LjUsMjIuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eTowLjU0NSIgZmlsbD0iIzEwMTAxMSIgZD0iTSAyNC41LDIyLjUgQyAyNi41ODY5LDIzLjU4NDYgMjcuOTIwMiwyNS4yNTEyIDI4LjUsMjcuNUMgMjguMTY2NywyOC4xNjY3IDI3LjgzMzMsMjguODMzMyAyNy41LDI5LjVDIDI2LjUsMjkuNSAyNS41LDI5LjUgMjQuNSwyOS41QyAyMy41OTk0LDI3LjI3MjkgMjEuOTMyOCwyNi4yNzI5IDE5LjUsMjYuNUMgMjEuMTQyMywyNS4xOTcgMjIuODA4OSwyMy44NjM3IDI0LjUsMjIuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eTowLjE0IiBmaWxsPSIjMDkwYzE1IiBkPSJNIDcuNSwyNS41IEMgMTEuNDY1OSwyNi4xNjIxIDE1LjQ2NTksMjYuNDk1NSAxOS41LDI2LjVDIDE4LjAzNiwyNy4xNTk5IDE2LjM2OTMsMjcuNDkzMiAxNC41LDI3LjVDIDExLjc5NTQsMjcuNjgzOSA5LjQ2MjEsMjcuMDE3MyA3LjUsMjUuNSBaIi8+PC9nPgo8L3N2Zz4K"
LABEL oc.keyword="qupath"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.gtk"
LABEL oc.name="qupath"
LABEL oc.launch="qupath.lib.gui.QuPathApp.qupath.lib.gui.QuPathApp"
LABEL oc.displayname="QuPath"
LABEL oc.path="/opt/qupath/QuPath/bin/QuPath"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.showinview=dock
LABEL oc.acl="{\"permit\":[\"all\"]}"

RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done

RUN mkdir -p /etc/localaccount
RUN for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

ENV APPNAME "qupath"
ENV APPBIN "/opt/qupath/QuPath/bin/QuPath"
ENV APP "/opt/qupath/QuPath/bin/QuPath"
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
CMD ["/composer/appli-docker-entrypoint.sh" ]


