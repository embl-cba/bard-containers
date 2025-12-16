FROM abcdesktopio/oc.user.ubuntu:3.2

USER root

RUN for f in passwd shadow group gshadow ; do rm -f /etc/$f; cp "$ABCDESKTOP_LOCALACCOUNT_DIR/$f" "/etc/$f"; done
RUN echo "Install here all packages you want"

RUN apt-get update &&  apt-get install -y --no-install-recommends ssh qterminal xfonts-base vim nano dnsutils iputils-ping git wget curl && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN for f in passwd shadow group gshadow ; do if [ -f /etc/$f ] ; then  cp /etc/$f $ABCDESKTOP_LOCALACCOUNT_DIR ; rm -f /etc/$f; ln -s $ABCDESKTOP_LOCALACCOUNT_DIR/$f /etc/$f; fi; done
