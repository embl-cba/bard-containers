ARG TAG=dev
FROM registry.git.embl.de/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8

USER root
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

ARG DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES all
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/lib/x86_64-linux-gnu
ENV VGL_DISPLAY egl0
ENV VGL_COMPRESS proxy
# Install locales 
RUN apt-get clean && \
    apt-get update && apt-get install --no-install-recommends -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install Xvfb and other important libraries or packages
RUN    apt-get update -y && apt-get install --no-install-recommends -y \
        konsole \
        software-properties-common \
        build-essential \
        curl \
        wget \
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
        xvfb
WORKDIR /tmp
ARG VIRTUALGL_VERSION=3.1
ARG VIRTUALGL_URL="https://sourceforge.net/projects/virtualgl/files"
RUN curl -fsSL -O "${VIRTUALGL_URL}/virtualgl_${VIRTUALGL_VERSION}_amd64.deb" && \
    apt-get update && apt-get install -y --no-install-recommends ./virtualgl_${VIRTUALGL_VERSION}_amd64.deb && \
    rm -f "virtualgl_${VIRTUALGL_VERSION}_amd64.deb" && \
    rm -rf /var/lib/apt/lists/* && \
    chmod u+s /usr/lib/libvglfaker.so && \
    chmod u+s /usr/lib/libdlfaker.so 

#Install ChimeraX
RUN apt-get update -y && apt-get install -y ffmpeg \
            xdg-utils \
            libasound2 \
            libffi7 \
            libfftw3-single3 \
            libgdk-pixbuf-2.0-0 \
            libgfortran5 \
            libgstreamer-plugins-base1.0-0 \
            libnspr4 \
            libnss3 \
            libopenjp2-7 \
            libosmesa6 \
            libpulse-mainloop-glib0 \
            libxcb-icccm4 \
            libxcb-image0 \
            libxcb-keysyms1 \
            libxcb-render-util0 \
            libxcb-util1 \
            libxcb-xinerama0 \
            libxkbcommon-x11-0 \
            tar
            
RUN mkdir /usr/local/chimera

WORKDIR /usr/local/chimera

COPY chimera-installer.bin /usr/local/chimera

RUN chmod +x chimera-installer.bin
RUN echo /usr/local/chimera/bin/ |./chimera-installer.bin
RUN ln -s /usr/local/chimera/bin/bin/* /usr/local/bin/


LABEL oc.icon="chimera.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZlcnNpb249IjEuMSIgd2lkdGg9IjUxMnB4IiBoZWlnaHQ9IjUxMnB4IiBzdHlsZT0ic2hhcGUtcmVuZGVyaW5nOmdlb21ldHJpY1ByZWNpc2lvbjsgdGV4dC1yZW5kZXJpbmc6Z2VvbWV0cmljUHJlY2lzaW9uOyBpbWFnZS1yZW5kZXJpbmc6b3B0aW1pemVRdWFsaXR5OyBmaWxsLXJ1bGU6ZXZlbm9kZDsgY2xpcC1ydWxlOmV2ZW5vZGQiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIj4KPGc+PHBhdGggc3R5bGU9Im9wYWNpdHk6MC4xMzUiIGZpbGw9IiMwMTAxMDEiIGQ9Ik0gMjAxLjUsLTAuNSBDIDIzOS41LC0wLjUgMjc3LjUsLTAuNSAzMTUuNSwtMC41QyAzNjUuMDAyLDExLjkwODIgNDA4LjE2OSwzOC4yNDE2IDQ0NSw3OC41QyA0NjguMDIxLDEwOC4wNTYgNDg0LjUyMSwxNDAuMjIzIDQ5NC41LDE3NUMgNTEzLjc5MSwyNTguOTUxIDQ5Ni42MjUsMzMzLjc4NSA0NDMsMzk5LjVDIDQzMy45Myw0MDcuNDQ3IDQyNS40Myw0MTUuOTQ3IDQxNy41LDQyNUMgNDA4LjAxMyw0MzIuNTc2IDM5OC4zNDYsNDM5LjkwOSAzODguNSw0NDdDIDM5My42MjcsNDQ5LjM5NyAzOTguNjI3LDQ1Mi4wNjQgNDAzLjUsNDU1QyA0MTUsNDY3LjgzMyA0MjcuMTY3LDQ4MCA0NDAsNDkxLjVDIDQ0NC4yNTcsNDk3LjY2NCA0NDUuNDIzLDUwNC4zMyA0NDMuNSw1MTEuNUMgNDI4LjE2Nyw1MTEuNSA0MTIuODMzLDUxMS41IDM5Ny41LDUxMS41QyAzNzEuOTAzLDUwMi4wMDkgMzQ2LjkwMyw0OTAuODQyIDMyMi41LDQ3OEMgMzE4LjE2Nyw0NzcuMzMzIDMxMy44MzMsNDc3LjMzMyAzMDkuNSw0NzhDIDI3MC45MjYsNDg1LjQ0OCAyMzIuNzU5LDQ4NC42MTUgMTk1LDQ3NS41QyAxNzYuNDI1LDQ2OS4yMDEgMTU3LjI1OCw0NjEuMDM1IDEzNy41LDQ1MUMgOTAuODY1Miw0MjIuOTA4IDU3Ljg2NTIsMzg2LjI0MiAzOC41LDM0MUMgMzQuMTk5OSwzMzQuODAxIDMxLjAzMzIsMzI3Ljk2OCAyOSwzMjAuNUMgOS4yMjU0LDI1OC42NSAxMS41NTg3LDE5Ny42NSAzNiwxMzcuNUMgMzYuNDQ4MiwxMzUuNzc2IDM3LjI4MTUsMTM1LjEwOSAzOC41LDEzNS41QyAzOC4xNjY3LDEzNC44MzMgMzcuODMzMywxMzQuMTY3IDM3LjUsMTMzLjVDIDM3Ljg0NTcsMTMyLjMwNCAzOC4zNDU3LDEzMi4zMDQgMzksMTMzLjVDIDM5LjQ2NDMsMTMyLjkwNiAzOS42MzEsMTMyLjIzOSAzOS41LDEzMS41QyA1Mi41MDYxLDEwNC4yNDMgNzEuMTcyNyw3OC43NDM1IDk1LjUsNTVDIDExMi40NjgsNDIuMDg3NyAxMjguMzAyLDMwLjkyMTEgMTQzLDIxLjVDIDE2MS41NzIsMTIuNTc0OCAxODEuMDcyLDUuMjQxNDQgMjAxLjUsLTAuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eToxIiBmaWxsPSIjYThkOWY0IiBkPSJNIDQ3Ni41LDE4My41IEMgNDc2LjYyNSwxOTAuMDk4IDQ3Ny42MjUsMTk2LjQzMSA0NzkuNSwyMDIuNUMgNDg2LjU2OCwyODEuMTM5IDQ2MS41NjgsMzQ3LjYzOSA0MDQuNSw0MDJDIDM4NS43NjgsNDE4LjcwNCAzNjQuNzY4LDQzMS44NyAzNDEuNSw0NDEuNUMgMzQwLjg1LDQ0MS44MDQgMzQwLjE4Myw0NDIuMTM3IDMzOS41LDQ0Mi41QyAzMjUuNTkxLDQzNy4yMSAzMTIuMjU3LDQzMC44NzcgMjk5LjUsNDIzLjVDIDMzMS42OTYsNDEwLjI0MyAzNTguMDMsMzg5LjU3NyAzNzguNSwzNjEuNUMgMzgzLjE1MSwzNTYuODcxIDM4Ni44MTgsMzUxLjUzNyAzODkuNSwzNDUuNUMgMzk2LjIwMSwzMzIuMDk3IDQwMi4zNjcsMzE4LjQzIDQwOCwzMDQuNUMgNDEyLjc3MiwyODguODA1IDQxNS45MzksMjcyLjgwNSA0MTcuNSwyNTYuNUMgNDE4LjY2LDI0My4zNCA0MTguODI3LDIzMC4wMDYgNDE4LDIxNi41QyA0MTcuNTY4LDIxMS41MDMgNDE2LjQwMSwyMDYuODM3IDQxNC41LDIwMi41QyA0MDMuOTYxLDE0Ny44MzQgMzc1Ljk2MSwxMDQuNjY3IDMzMC41LDczQyAyODMuNTE2LDQzLjQ0OTIgMjMzLjE4MywzNi4xMTU4IDE3OS41LDUxQyAxMTUuODI0LDc0LjE3MzQgNzMuODI0NCwxMTguMDA3IDUzLjUsMTgyLjVDIDUwLjQ0NzUsMTg5Ljc1MyA0OC43ODA4LDE5Ny40MiA0OC41LDIwNS41QyAzOC45MTA5LDI3Mi4xOCA1Ni40MTA5LDMzMC41MTQgMTAxLDM4MC41QyAxNDMuMTA0LDQyMi40ODQgMTkzLjkzOCw0NDAuODE3IDI1My41LDQzNS41QyAyNTcuMTgyLDQzNS42NjUgMjYwLjg0OCw0MzUuNDk5IDI2NC41LDQzNUMgMjY1LjQxNiw0MzQuNzIyIDI2Ni4wODIsNDM0LjIyMiAyNjYuNSw0MzMuNUMgMjcwLjI2Miw0MzMuMzA5IDI3My45MjksNDMyLjY0MiAyNzcuNSw0MzEuNUMgMjg5LjYwNiw0MzcuNzIxIDMwMS42MDYsNDQ0LjIyMSAzMTMuNSw0NTFDIDMxMi4yNjMsNDUxLjIzMiAzMTEuMjYzLDQ1MS43MzIgMzEwLjUsNDUyLjVDIDIyMS44MjcsNDcyLjA0OSAxNDUuOTk0LDQ0OS4zODIgODMsMzg0LjVDIDMwLjU1MTQsMzIyLjcwMiAxMy4yMTgxLDI1Mi4wMzUgMzEsMTcyLjVDIDQ2LjY5NjksMTE0LjkxOCA3OS4xOTY5LDY5LjQxODUgMTI4LjUsMzZDIDE4OS43MTUsLTEuMjQ3MzIgMjU0LjcxNSwtOS41ODA2NSAzMjMuNSwxMUMgNDA1LjQzLDQxLjA5NTEgNDU2LjQzLDk4LjU5NTEgNDc2LjUsMTgzLjUgWiIvPjwvZz4KPGc+PHBhdGggc3R5bGU9Im9wYWNpdHk6MC4wNSIgZmlsbD0iIzAwMDAwMCIgZD0iTSA0MTQuNSwyMDIuNSBDIDQxNy4xMzUsMjIwLjM4NiA0MTguMTM1LDIzOC4zODYgNDE3LjUsMjU2LjVDIDQxNS45MzksMjcyLjgwNSA0MTIuNzcyLDI4OC44MDUgNDA4LDMwNC41QyA0MDIuMzY3LDMxOC40MyAzOTYuMjAxLDMzMi4wOTcgMzg5LjUsMzQ1LjVDIDM0NS45NzMsMzE0LjU0MyAyOTkuOTczLDI4Ny4zNzcgMjUxLjUsMjY0QyAyNDkuMTg4LDI0OC4zNTUgMjQwLjE4OCwyNDEuMDIyIDIyNC41LDI0MkMgMjIwLjg5OSwyNDMuMzg3IDIxNy4zOTksMjQ0Ljg4NyAyMTQsMjQ2LjVDIDE4Ni40NDgsMjM1LjA5NSAxNTcuOTQ4LDIyNi45MjggMTI4LjUsMjIyQyAxMTkuMTY3LDIyMS4zMzMgMTA5LjgzMywyMjEuMzMzIDEwMC41LDIyMkMgNzkuOTAwNCwyMjcuMDU2IDczLjczMzcsMjM5LjU1NiA4MiwyNTkuNUMgODUuOTg5NSwyNjguODIgOTAuOTg5NSwyNzcuNDg3IDk3LDI4NS41QyAxMDUuNTg4LDI5Ni43NTkgMTE0LjkyMSwzMDcuNDI2IDEyNSwzMTcuNUMgMTcxLjcwMiwzNjEuMjQyIDIyMi41MzUsMzk5LjI0MiAyNzcuNSw0MzEuNUMgMjczLjkyOSw0MzIuNjQyIDI3MC4yNjIsNDMzLjMwOSAyNjYuNSw0MzMuNUMgMjYxLjk3Miw0MzMuNzcgMjU3LjYzOSw0MzQuNDM3IDI1My41LDQzNS41QyAxOTMuOTM4LDQ0MC44MTcgMTQzLjEwNCw0MjIuNDg0IDEwMSwzODAuNUMgNTYuNDEwOSwzMzAuNTE0IDM4LjkxMDksMjcyLjE4IDQ4LjUsMjA1LjVDIDUwLjI5MjgsMTk3Ljk4MSA1MS45NTk0LDE5MC4zMTQgNTMuNSwxODIuNUMgNzMuODI0NCwxMTguMDA3IDExNS44MjQsNzQuMTczNCAxNzkuNSw1MUMgMjMzLjE4MywzNi4xMTU4IDI4My41MTYsNDMuNDQ5MiAzMzAuNSw3M0MgMzc1Ljk2MSwxMDQuNjY3IDQwMy45NjEsMTQ3LjgzNCA0MTQuNSwyMDIuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eTowLjAwNCIgZmlsbD0iIzAwMDAwMCIgZD0iTSAzOS41LDEzMS41IEMgMzguODMzMywxMzAuMTY3IDM4LjgzMzMsMTMwLjE2NyAzOS41LDEzMS41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjAuODYzIiBmaWxsPSIjNzg5YWFkIiBkPSJNIDUzLjUsMTgyLjUgQyA1MS45NTk0LDE5MC4zMTQgNTAuMjkyOCwxOTcuOTgxIDQ4LjUsMjA1LjVDIDQ4Ljc4MDgsMTk3LjQyIDUwLjQ0NzUsMTg5Ljc1MyA1My41LDE4Mi41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjAuOTI5IiBmaWxsPSIjNjU4MjkyIiBkPSJNIDQ3Ni41LDE4My41IEMgNDc4LjQ1MywxODkuNTU2IDQ3OS40NTMsMTk1Ljg4OSA0NzkuNSwyMDIuNUMgNDc3LjYyNSwxOTYuNDMxIDQ3Ni42MjUsMTkwLjA5OCA0NzYuNSwxODMuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eTowLjg0NyIgZmlsbD0iIzhmYjlkMCIgZD0iTSA0MTQuNSwyMDIuNSBDIDQxNi40MDEsMjA2LjgzNyA0MTcuNTY4LDIxMS41MDMgNDE4LDIxNi41QyA0MTguODI3LDIzMC4wMDYgNDE4LjY2LDI0My4zNCA0MTcuNSwyNTYuNUMgNDE4LjEzNSwyMzguMzg2IDQxNy4xMzUsMjIwLjM4NiA0MTQuNSwyMDIuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eTowLjk5NiIgZmlsbD0iIzJlMjgyOSIgZD0iTSAzODkuNSwzNDUuNSBDIDM4Ni44MTgsMzUxLjUzNyAzODMuMTUxLDM1Ni44NzEgMzc4LjUsMzYxLjVDIDM3OC40ODksMzU5Ljk4MyAzNzcuODIzLDM1OC44MTYgMzc2LjUsMzU4QyAzMzYuMDY1LDMyNS44NTMgMjkxLjg5OCwyOTkuNjg2IDI0NCwyNzkuNUMgMjQwLjc3MywyODAuODY0IDIzNy42MDYsMjgyLjM2NCAyMzQuNSwyODRDIDIyMC43MDYsMjg2LjI4MyAyMTIuMDM5LDI4MC43ODMgMjA4LjUsMjY3LjVDIDE5My43NDEsMjYzLjYxNCAxNzguNzQxLDI2Mi4xMTQgMTYzLjUsMjYzQyAxNDYuNjUxLDI2Ni41MzMgMTQxLjE1MSwyNzYuMzY3IDE0NywyOTIuNUMgMTUzLjMzMywzMDYuNTAzIDE2MS42NjYsMzE5LjE3IDE3MiwzMzAuNUMgMjA5LjQ3NywzNjguNDc4IDI1MS45NzcsMzk5LjQ3OCAyOTkuNSw0MjMuNUMgMzEyLjI1Nyw0MzAuODc3IDMyNS41OTEsNDM3LjIxIDMzOS41LDQ0Mi41QyAzNDAuMTgzLDQ0Mi4xMzcgMzQwLjg1LDQ0MS44MDQgMzQxLjUsNDQxLjVDIDM0Mi41NzQsNDQzLjI4NCAzNDQuMjQsNDQ0LjQ1MSAzNDYuNSw0NDVDIDM1OC45ODYsNDQ5LjI4OCAzNzEuNjUzLDQ1Mi45NTUgMzg0LjUsNDU2QyAzOTguNSw0NzAgNDEyLjUsNDg0IDQyNi41LDQ5OEMgMzg3LjU5MSw0ODYuNzk5IDM1MC40MjQsNDcxLjI5OSAzMTUsNDUxLjVDIDMxMy42NDQsNDUyLjM4IDMxMi4xNDQsNDUyLjcxNCAzMTAuNSw0NTIuNUMgMzExLjI2Myw0NTEuNzMyIDMxMi4yNjMsNDUxLjIzMiAzMTMuNSw0NTFDIDMwMS42MDYsNDQ0LjIyMSAyODkuNjA2LDQzNy43MjEgMjc3LjUsNDMxLjVDIDIyMi41MzUsMzk5LjI0MiAxNzEuNzAyLDM2MS4yNDIgMTI1LDMxNy41QyAxMTQuOTIxLDMwNy40MjYgMTA1LjU4OCwyOTYuNzU5IDk3LDI4NS41QyA5MC45ODk1LDI3Ny40ODcgODUuOTg5NSwyNjguODIgODIsMjU5LjVDIDczLjczMzcsMjM5LjU1NiA3OS45MDA0LDIyNy4wNTYgMTAwLjUsMjIyQyAxMDkuODMzLDIyMS4zMzMgMTE5LjE2NywyMjEuMzMzIDEyOC41LDIyMkMgMTU3Ljk0OCwyMjYuOTI4IDE4Ni40NDgsMjM1LjA5NSAyMTQsMjQ2LjVDIDIxNy4zOTksMjQ0Ljg4NyAyMjAuODk5LDI0My4zODcgMjI0LjUsMjQyQyAyNDAuMTg4LDI0MS4wMjIgMjQ5LjE4OCwyNDguMzU1IDI1MS41LDI2NEMgMjk5Ljk3MywyODcuMzc3IDM0NS45NzMsMzE0LjU0MyAzODkuNSwzNDUuNSBaIi8+PC9nPgo8Zz48cGF0aCBzdHlsZT0ib3BhY2l0eTowLjA2OCIgZmlsbD0iIzAwMDAwMCIgZD0iTSAzNzguNSwzNjEuNSBDIDM1OC4wMywzODkuNTc3IDMzMS42OTYsNDEwLjI0MyAyOTkuNSw0MjMuNUMgMjUxLjk3NywzOTkuNDc4IDIwOS40NzcsMzY4LjQ3OCAxNzIsMzMwLjVDIDE2MS42NjYsMzE5LjE3IDE1My4zMzMsMzA2LjUwMyAxNDcsMjkyLjVDIDE0MS4xNTEsMjc2LjM2NyAxNDYuNjUxLDI2Ni41MzMgMTYzLjUsMjYzQyAxNzguNzQxLDI2Mi4xMTQgMTkzLjc0MSwyNjMuNjE0IDIwOC41LDI2Ny41QyAyMTIuMDM5LDI4MC43ODMgMjIwLjcwNiwyODYuMjgzIDIzNC41LDI4NEMgMjM3LjYwNiwyODIuMzY0IDI0MC43NzMsMjgwLjg2NCAyNDQsMjc5LjVDIDI5MS44OTgsMjk5LjY4NiAzMzYuMDY1LDMyNS44NTMgMzc2LjUsMzU4QyAzNzcuODIzLDM1OC44MTYgMzc4LjQ4OSwzNTkuOTgzIDM3OC41LDM2MS41IFoiLz48L2c+CjxnPjxwYXRoIHN0eWxlPSJvcGFjaXR5OjAuNzczIiBmaWxsPSIjNmY4ZmEwIiBkPSJNIDI2Ni41LDQzMy41IEMgMjY2LjA4Miw0MzQuMjIyIDI2NS40MTYsNDM0LjcyMiAyNjQuNSw0MzVDIDI2MC44NDgsNDM1LjQ5OSAyNTcuMTgyLDQzNS42NjUgMjUzLjUsNDM1LjVDIDI1Ny42MzksNDM0LjQzNyAyNjEuOTcyLDQzMy43NyAyNjYuNSw0MzMuNSBaIi8+PC9nPgo8L3N2Zz4K"
LABEL oc.keyword="chimera,imaging"
LABEL oc.cat="development"
LABEL oc.desktopfile="org.kde.konsole.desktop"
LABEL oc.launch="chimera.konsole"
LABEL oc.template="registry.git.embl.de/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8"
ENV ARGS="--name chimeraubuntu --hold -e vglrun -c proxy /usr/local/bin/chimera"
LABEL oc.name="chimeraubuntu"
LABEL oc.displayname="Chimera v1.17.3"
LABEL oc.path="/usr/bin/konsole"
LABEL oc.type=app
#LABEL oc.showinview="dock"
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"

RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done
ENV APPNAME "chimeraubuntu"
ENV APPBIN "/usr/bin/konsole"
LABEL oc.args="--name chimeraubuntu --hold -e vglrun -c proxy /usr/local/bin/chimera"
ENV APP "/usr/bin/konsole"

RUN mkdir -p /run/user
RUN chmod 777 /run/user
USER root
RUN mkdir -p /etc/localaccount
RUN for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done


USER balloon

CMD [ "/composer/appli-docker-entrypoint.sh" ]
