FROM abcdesktopio/oc.template.rockylinux.nvidia.8:3.2

RUN set -ex \
    && yum makecache \
    && yum -y update \
    && yum -y install dnf-plugins-core \
    && yum config-manager --set-enabled powertools \
    && yum -y install \
       wget \
       bzip2 \
       perl \
       gcc \
       gcc-c++\
       git \
       gnupg \
       make \
       munge \
       munge-devel \
       python3-devel \
       python3-pip \
       python3 \
       mariadb-server \
       mariadb-devel \
       psmisc \
       bash-completion \
       vim-enhanced \
       http-parser-devel \
       json-c-devel \
    && yum clean all \
    && rm -rf /var/cache/yum

RUN yum install -y epel-release && yum install -y supervisor konsole qt5-qtsvg

RUN alternatives --set python /usr/bin/python3 && pip3 install Cython pytest

ARG GOSU_VERSION=1.17

# Add Tini
ENV TINI_VERSION v0.19.0
ENV TINI_SUBREAPER=1

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini.asc /tini.asc
RUN gpg --batch --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
 && gpg --batch --verify /tini.asc /tini && chmod +x /tini

RUN set -ex \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-amd64.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -rf "${GNUPGHOME}" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true

ARG SLURM_TAG=slurm-22-05-8-1
ARG JOBS=4
RUN set -ex \
    && git clone -b ${SLURM_TAG} --single-branch --depth=1 https://github.com/SchedMD/slurm.git \
    && pushd slurm \
    && ./configure --prefix=/usr --sysconfdir=/etc/slurm \
        --with-mysql_config=/usr/bin --libdir=/usr/lib64 --enable-multiple-slurmd \
    && sed -e 's|#!/usr/bin/env python3|#!/usr/bin/python|' -i doc/html/shtml2html.py \
    && make -j ${JOBS} install \
    && install -D -m644 etc/cgroup.conf.example /etc/slurm/cgroup.conf.example \
    && install -D -m644 etc/slurm.conf.example /etc/slurm/slurm.conf.example \
    && install -D -m600 etc/slurmdbd.conf.example /etc/slurm/slurmdbd.conf.example \
    && install -D -m644 contribs/slurm_completion_help/slurm_completion.sh /etc/profile.d/slurm_completion.sh \
    && popd \
    && rm -rf slurm \
    && groupadd -r slurm  \
    && useradd -r -g slurm slurm \
    && mkdir -p /etc/sysconfig/slurm \
        /var/spool/slurmd \
        /var/spool/slurmctld \
        /var/log/slurm \
        /var/run/slurm \
    && chown -R slurm:slurm /var/spool/slurmd \
        /var/spool/slurmctld \
        /var/log/slurm \
        /var/run/slurm \
    && /sbin/create-munge-key

RUN dd if=/dev/random of=/etc/slurm/jwt_hs256.key bs=32 count=1 \
    && chmod 600 /etc/slurm/jwt_hs256.key && chown slurm:slurm /etc/slurm/jwt_hs256.key

RUN chmod -R 777 /var/spool/slurmctld /var/run/slurm /etc/slurm /var/log/slurm && chmod 777 /etc/hostname

COPY --chown=slurm files/slurm/slurm.conf files/slurm/slurmdbd.conf files/slurm/cgroup.conf /etc/slurm/
COPY files/supervisord.conf /etc/

RUN chmod 0600 /etc/slurm/slurmdbd.conf


COPY init-slurm.sh /usr/local/bin/init-slurm.sh
COPY startup.sh /usr/local/bin/startup.sh
RUN  chmod +x /usr/local/bin/init-slurm.sh && chmod +x /usr/local/bin/startup.sh

LABEL oc.icon="konsole.svg"
LABEL oc.icondata="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgd2lkdGg9IjEyOCIgaGVpZ2h0PSIxMjgiPgogIDxkZWZzPgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJvIiB4Mj0iMSIgeTI9IjEiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiMxMTEiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjNTU1Ii8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJuIiB4MT0iNTUuOTUiIHgyPSI1NS45NSIgeTE9IjgxIiB5Mj0iODAiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMS4wODggMCAwIDEgMy4zNjQgMTYpIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCIgc3RvcC1jb2xvcj0iI0ZGRiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNFRUUiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9ImIiIHgxPSI0NCIgeDI9IjQ0IiB5MT0iNDQiIHkyPSI0MCIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPgogICAgICA8c3RvcCBvZmZzZXQ9Ii41IiBzdG9wLWNvbG9yPSIjRkZGIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI0VFRUVFQyIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iYSIgeDE9IjI0IiB4Mj0iMjQiIHkxPSI0MCIgeTI9IjIwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CiAgICAgIDxzdG9wIG9mZnNldD0iLjUiIHN0b3AtY29sb3I9IiNGRkYiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjRUVFRUVDIi8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJoIiB4MT0iOSIgeDI9IjEwNi41NiIgeTE9IjI0LjMyIiB5Mj0iNTMuNjYiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjNTU1NzUzIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iLjYzIiBzdG9wLWNvbG9yPSIjMkUyRTJFIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzJFMkUyRSIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZyIgeDE9IjU2IiB4Mj0iNTYiIHkxPSI4MSIgeTI9IjciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMS4wODIgMCAwIDEuMDE0IDMuNDMgNy45MDUpIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCIgc3RvcC1jb2xvcj0iI0JCQiIvPgogICAgICA8c3RvcCBvZmZzZXQ9Ii41OSIgc3RvcC1jb2xvcj0iIzlGOUY5RiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM4ODgiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8bGluZWFyR3JhZGllbnQgeGxpbms6aHJlZj0iI2EiIGlkPSJpIiB4MT0iMjQiIHgyPSIyNCIgeTE9IjQwIiB5Mj0iMjAiIGdyYWRpZW50VHJhbnNmb3JtPSJ0cmFuc2xhdGUoNCAxNikiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIi8+CiAgICA8bGluZWFyR3JhZGllbnQgeGxpbms6aHJlZj0iI2IiIGlkPSJqIiB4MT0iNDQiIHgyPSI0NCIgeTE9IjQ0IiB5Mj0iNDAiIGdyYWRpZW50VHJhbnNmb3JtPSJ0cmFuc2xhdGUoNCAxNikiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIi8+CiAgICA8bGluZWFyR3JhZGllbnQgeGxpbms6aHJlZj0iI2EiIGlkPSJsIiB4MT0iMjQiIHgyPSIyNCIgeTE9IjQwIiB5Mj0iMjAiIGdyYWRpZW50VHJhbnNmb3JtPSJ0cmFuc2xhdGUoNCAxNikiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIi8+CiAgICA8bGluZWFyR3JhZGllbnQgeGxpbms6aHJlZj0iI2MiIGlkPSJmIiB4MT0iOCIgeDI9IjEyMCIgeTE9IjQwLjY3IiB5Mj0iNjQiIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMSAwIDAgMS4wOCAwIC05LjE4OCkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIi8+CiAgICA8bGluZWFyR3JhZGllbnQgeGxpbms6aHJlZj0iI2QiIGlkPSJwIiB4MT0iNjQiIHgyPSI2NCIgeTE9IjE3LjM2IiB5Mj0iNjUuODciIGdyYWRpZW50VHJhbnNmb3JtPSJtYXRyaXgoMSAwIDAgMS4wOCAwIC05LjE4OCkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIi8+CiAgICA8ZmlsdGVyIGlkPSJrIiB3aWR0aD0iMS4xMiIgaGVpZ2h0PSIxLjQ4IiB4PSItLjEiIHk9Ii0uMiI+CiAgICAgIDxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249Ii40Ii8+CiAgICA8L2ZpbHRlcj4KICAgIDxmaWx0ZXIgaWQ9Im0iIHdpZHRoPSIxLjIyIiBoZWlnaHQ9IjEuMTciIHg9Ii0uMSIgeT0iLS4xIj4KICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0iLjcyIi8+CiAgICA8L2ZpbHRlcj4KICAgIDxmaWx0ZXIgaWQ9ImUiPgogICAgICA8ZmVHYXVzc2lhbkJsdXIgc3RkRGV2aWF0aW9uPSIyLjA4Ii8+CiAgICA8L2ZpbHRlcj4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iZCIgY3g9IjUyIiBjeT0iLTMxIiByPSIxMzYiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZmZmIi8+CiAgICAgIDxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI2ZmZiIgc3RvcC1vcGFjaXR5PSIwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJjIiBjeD0iNTIiIGN5PSItMzEiIHI9IjEzNiIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiNjNmM2YzYiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIuNTIiIHN0b3AtY29sb3I9IiNFRUUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjYzZjNmM2Ii8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogIDwvZGVmcz4KICA8cGF0aCBkPSJNMyAwQzEuNCAwIDAgMS40IDAgM3Y5MGMwIDEuNiAxLjQgMyAzIDNoMTA2YzEuNiAwIDMtMS40IDMtM1YzYzAtMS42LTEuNC0zLTMtM0gzeiIgZmlsdGVyPSJ1cmwoI2UpIiBvcGFjaXR5PSIuNSIgdHJhbnNmb3JtPSJtYXRyaXgoMS4wMzYgMCAwIDEuMTM1IDYgNykiLz4KICA8cGF0aCBmaWxsPSJ1cmwoI2YpIiBkPSJNMTEgOGMtMS42IDAtMyAxLjUtMyAzLjN2OTdjMCAyIDEuNCAzLjQgMyAzLjRoMTA2YzEuNiAwIDMtMS41IDMtMy4zdi05N2MwLTItMS40LTMuMy0zLTMuM0gxMXoiLz4KICA8cGF0aCBmaWxsPSJ1cmwoI2cpIiBkPSJNMTIgMTVjLS41IDAtMSAuNS0xIDF2NzNjMCAuNi41IDEgMSAxaDEwNGMuNSAwIDEtLjUgMS0xVjE2YzAtLjYtLjUtMS0xLTFIMTJ6Ii8+CiAgPHBhdGggZD0iTTEyIDE2aDEwNHY4MEgxMnoiLz4KICA8cGF0aCBmaWxsPSJ1cmwoI2gpIiBkPSJNMTAzIDc2YzAgMS42LTEuNCAzLTMgM0gxMmMtMS42IDAtMy0xLjQtMy0zVjEyYzAtMS42IDEuNC0zIDMtM2g4OGMxLjYgMCAzIDEuNCAzIDN2NjR6IiB0cmFuc2Zvcm09Im1hdHJpeCgxLjA4NSAwIDAgMS4xMTQgMy4yMzQgNi45NykiLz4KICA8cGF0aCBmaWxsPSIjZmZmIiBkPSJNMTMgNTNjNDItMjIuNCA4Mi4yLTI3LjYgMTAyLTI4LjdWMTdIMTN2MzZ6IiBvcGFjaXR5PSIuMDUiLz4KICA8cGF0aCBmaWxsPSJ1cmwoI2kpIiBkPSJtMzYgNDgtMTYgOHYtNC4zTDMwLjcgNDYgMjAgNDAuM1YzNmwxNiA4LjNWNDh6IiBvcGFjaXR5PSIuOSIvPgogIDxwYXRoIGZpbGw9InVybCgjaikiIGQ9Ik01NiA2MEg0MHYtNGgxNnY0eiIgb3BhY2l0eT0iLjkiLz4KICA8cGF0aCBmaWxsPSIjZmZmIiBkPSJNNjAgNjBINDR2LTRoMTZ2NHoiIGZpbHRlcj0idXJsKCNrKSIgb3BhY2l0eT0iLjIiIHRyYW5zZm9ybT0ibWF0cml4KDEuMTI1IDAgMCAxLjUgLTEwLjUgLTI5KSIvPgogIDxwYXRoIGZpbGw9InVybCgjbCkiIGQ9Im0zNiA0OC0xNiA4di00LjNMMzAuNyA0NiAyMCA0MC4zVjM2bDE2IDguM1Y0OHoiIGZpbHRlcj0idXJsKCNtKSIgb3BhY2l0eT0iLjQiLz4KICA8cGF0aCBmaWxsPSJ1cmwoI24pIiBkPSJtMTE3LjIgOTYuNy0uNi0uN0gxMmwtLjguNmMuMi4yLjUuNC44LjRoMTA0LjVjLjMgMCAuNSAwIC43LS4zeiIvPgogIDxnIGZpbGw9InVybCgjbykiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDggMTUpIj4KICAgIDxjaXJjbGUgY3g9IjEwMSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIxMDQiIGN5PSI4OSIgcj0iMSIvPgogICAgPGNpcmNsZSBjeD0iMTAzIiBjeT0iOTIiIHI9IjEiLz4KICAgIDxjaXJjbGUgY3g9Ijk3IiBjeT0iODYiIHI9IjEiLz4KICAgIDxjaXJjbGUgY3g9IjEwMCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5MyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5OSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5NiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5NSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4OSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5MiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4NSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5MSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4OCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4NyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4MSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4NCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3NyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4MyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI4MCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3OSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3MyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3NiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2OSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3NSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3MiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI3MSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2NSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2OCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2MSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2NyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2NCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2MyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1NyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI2MCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1MyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1OSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1NiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1NSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0OSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1MiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0NSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI1MSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0OCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0NyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0MSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0NCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzNyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0MyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI0MCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzOSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzMyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzNiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyOSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzNSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzMiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIzMSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyNSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyOCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyMSIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyNyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyNCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyMyIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIxNyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIyMCIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIxMyIgY3k9Ijg2IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIxOSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIxNiIgY3k9Ijg5IiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSIxNSIgY3k9IjkyIiByPSIxIi8+CiAgICA8Y2lyY2xlIGN4PSI5IiBjeT0iODYiIHI9IjEiLz4KICAgIDxjaXJjbGUgY3g9IjEyIiBjeT0iODkiIHI9IjEiLz4KICAgIDxjaXJjbGUgY3g9IjExIiBjeT0iOTIiIHI9IjEiLz4KICAgIDxjaXJjbGUgY3g9IjgiIGN5PSI4OSIgcj0iMSIvPgogIDwvZz4KICA8cGF0aCBmaWxsPSJ1cmwoI3ApIiBkPSJNMTEgOGMtMS42IDAtMyAxLjUtMyAzLjN2OTdjMCAxIC40IDIgMSAyLjZWMTIuM2MwLTEuOCAxLjMtMy4yIDMtMy4yaDEwNGMxLjcgMCAzIDEuNCAzIDMuMi43IDI1IDAgOTguMiAwIDk4LjJ2LjNjLjYtLjcgMS0xLjYgMS0yLjV2LTk3YzAtMS44LTEuNC0zLjItMy0zLjJIMTF6IiBvcGFjaXR5PSIuOSIvPgo8L3N2Zz4="
LABEL oc.keyword="konsole, slurm,bash,shell"
LABEL oc.cat="development"
LABEL oc.launch="slurm.konsole"
LABEL oc.template="abcdesktopio/oc.template.rockylinux.nvidia.8"
LABEL oc.name="slurm"
LABEL oc.displayname="Slurm Konsole"
LABEL oc.path="/usr/bin/konsole"
LABEL oc.args="--hold -e bash --rcfile /usr/local/bin/startup.sh"
LABEL oc.type=app
LABEL oc.rules="{\"homedir\":{\"default\":true}}"
LABEL oc.acl="{\"permit\":[\"all\"]}"
LABEL oc.showinview=dock

RUN  if [ -d /usr/share/icons ]   && [ -x /composer/safelinks.sh ] && [ -d /usr/share/icons   ];  then cd /usr/share/icons;    /composer/safelinks.sh; fi \
    && if [ -d /usr/share/pixmaps ] && [ -x /composer/safelinks.sh ] && [ -d /usr/share/pixmaps ];  then cd /usr/share/pixmaps;  /composer/safelinks.sh; fi 

ENV APPNAME "slurm"
ENV APPBIN "/usr/bin/konsole"
ENV APP "/usr/bin/konsole"
ENV ARGS="--hold -e bash --rcfile /usr/local/bin/startup.sh"
ENV NVIDIA_DRIVER_CAPABILITIES "compute,utility"

RUN mkdir -p /run/user \
    && chmod 777 /run/user \
    && mkdir -p /etc/localaccount \
    && for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f /etc/localaccount; rm -f /etc/$f; ln -s /etc/localaccount/$f /etc/$f; fi; done


CMD [ "/composer/appli-docker-entrypoint.sh" ]
#CMD ["/usr/bin/konsole --hold", "-e", "bash", "--rcfile", "/usr/local/bin/startup.sh"]
#ENTRYPOINT ["/usr/bin/konsole", "--hold", "-e", "bash", "--rcfile", "/usr/local/bin/startup.sh"]

