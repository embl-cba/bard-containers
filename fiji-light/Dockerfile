FROM registry.git.embl.org/grp-cbbcs/abcdesktop-apps/base-image:ubuntu22-cuda-11-8

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
    apt-get install -y unzip wget build-essential git software-properties-common libxi6 libxrender1 libxtst6 libfreetype6 fonts-dejavu fontconfig nvidia-opencl-dev ocl-icd-opencl-dev && \
     echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

#RUN wget -O /tmp/fiji-linux64.zip https://downloads.imagej.net/fiji/latest/fiji-linux64.zip && unzip /tmp/fiji-linux64.zip -d /usr/local/
RUN wget -O /tmp/fiji-linux64.zip https://downloads.imagej.net/fiji/archive/20241226-1317/fiji-linux64.zip && unzip /tmp/fiji-linux64.zip -d /usr/local/

RUN mv /usr/local/Fiji.app /usr/local/Fiji && \
    chmod -R 0777 /usr/local/Fiji/lib && \
    mkdir /usr/local/Fiji/models && \
    chmod -R 777 /usr/local/Fiji/models

COPY ImageJ.cfg /usr/local/Fiji/ImageJ.cfg

LABEL oc.icon="fiji_icon.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiICAKICAgeG1sbnM6aW5rc2NhcGU9Imh0dHA6Ly93d3cuaW5rc2NhcGUub3JnL25hbWVzcGFjZXMvaW5rc2NhcGUiCiAgIHdpZHRoPSIxMzIiIGhlaWdodD0iMTMyLjE1MDI0Ij4KICA8ZGVmcz4KICAgIDxmaWx0ZXIKICAgICAgIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0ic1JHQiIKICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgIGlkPSJmaWx0ZXI0MzIzNC04Ij4KICAgICAgPGZlR2F1c3NpYW5CbHVyCiAgICAgICAgIGlua3NjYXBlOmNvbGxlY3Q9ImFsd2F5cyIKICAgICAgICAgc3RkRGV2aWF0aW9uPSIxNS45NTM1MDQiCiAgICAgICAgIGlkPSJmZUdhdXNzaWFuQmx1cjQzMjM2LTYiIC8+CiAgICA8L2ZpbHRlcj4KICAgIDxwYXRoIGlkPSJNYWluIgogICAgICAgZD0ibSA0OTUuNjQxNDQsMTQ0Ni4yNSA1NS44NTg1NiwwIC0wLjY0NjQ1LDI4NC45NTUyIC0xNjkuMDM1MjcsMCAwLC01Ni44NjE0IDExMy44MjMxNiwtMC4wOTQgeiBtIDExMy44NTg1NiwwIDU2LDAgLTAuNjQ2NDUsMTcwLjk1NTIgLTU1LDAgeiBtIC0yMjgsMCA1NiwwIC0wLjY0NjQ1LDE3MC45NTUyIC01NSwwIHogbSAtNTcuOTk4NjUsMjgzLjk0ODQgLTU2LjU2ODU0LDAuNzA3MSAwLjcwNzExLC0zOTguODA4MyAzOTcuMzYwMDgsMC43Nzc4IDAsNTYuNSAtMzQwLjYxNDc2LC0wLjE3ODkgeiIvPgogIDwvZGVmcz4KICA8bWV0YWRhdGE+CiAgICA8cmRmOlJERj4KICAgICAgPGNjOldvcmsgcmRmOmFib3V0PSIiPgogICAgICAgIDxkYzpmb3JtYXQ+aW1hZ2Uvc3ZnK3htbDwvZGM6Zm9ybWF0PgogICAgICAgIDxkYzp0eXBlIHJkZjpyZXNvdXJjZT0iaHR0cDovL3B1cmwub3JnL2RjL2RjbWl0eXBlL1N0aWxsSW1hZ2UiIC8+CiAgICAgICAgPGRjOnRpdGxlPjwvZGM6dGl0bGU+CiAgICAgIDwvY2M6V29yaz4KICAgIDwvcmRmOlJERj4KICA8L21ldGFkYXRhPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02My41MTk4MiwtMzU5LjQzMzY4KXNjYWxlKDAuMjc3ODEwNTEsMC4yNzc4MTA1MSkiPgogICAgPHVzZSB4bGluazpocmVmPSIjTWFpbiIgc3R5bGU9ImZpbGw6IzAwMDAwMDtmaWx0ZXI6dXJsKCNmaWx0ZXI0MzIzNC04KSIvPgogICAgPHVzZSB4bGluazpocmVmPSIjTWFpbiIgc3R5bGU9ImZpbGw6IzY0YTRlMiIvPgogIDwvZz4KPC9zdmc+"
LABEL oc.keyword="fiji"
LABEL oc.cat="development"
LABEL oc.template="abcdesktopio/oc.template.gtk"
LABEL oc.name="fiji-light"
LABEL oc.launch="fiji-light.net-imagej-launcher-ClassLauncher"
LABEL oc.displayname="Fiji (vanila)"
LABEL oc.path="/usr/local/Fiji/ImageJ-linux64"
LABEL oc.args="-Dij2.plugin.dirs=/usr/local/Fiji/jars:/usr/local/Fiji.app/plugins:/home/`whoami`/.plugins"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.showinview=dock
LABEL oc.acl="{\"permit\":[\"all\"]}"

RUN for d in /usr/share/icons /usr/share/pixmaps ; do echo "testing link in $d"; if [ -d $d ] && [ -x /composer/safelinks.sh ] ; then echo "fixing link in $d"; cd $d ; /composer/safelinks.sh ; fi; done

RUN mkdir -p /etc/localaccount
RUN for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done

ENV APPNAME "Fiji"
ENV APPBIN "/usr/local/Fiji/ImageJ-linux64"
ENV APP "/usr/local/Fiji/ImageJ-linux64"
ENV ARGS "-Dij2.plugin.dirs=/usr/local/Fiji.app/jars:/usr/local/Fiji.app/plugins:/home/`whoami`/.plugins"
ENV FIJIPATH="/user/local/Fiji"
ENV PATH=$FIJIPATH:$PATH

CMD ["/composer/appli-docker-entrypoint.sh" ]


