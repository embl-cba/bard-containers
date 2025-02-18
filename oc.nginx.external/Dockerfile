#
# --- update oc.nginx:builder image start here ---
# use the abcdesktopio/oc.nginx:builder
# oc.nginx:builder contains Makefile and tools like nodejs, lessc need to update the ui.json file
# oc.nginx:builder source https://raw.githubusercontent.com/abcdesktopio/oc.nginx/main/Dockerfile.builder          
#######
FROM abcdesktopio/oc.nginx:builder as builder
# copy data files /var/webModules
#COPY --from=abcdesktopio/oc.nginx:3.2 var/webModules /var/webModules
# copy updated file ui.json with your own custom values
#COPY ui.json /var/webModules/transpile/config/

RUN git clone https://git.embl.de/grp-cbbcs/webModules-external.git /var/webModules

# run makefile
# make dev (for dev)
# make prod (for prod)
RUN cd /var/webModules && make dev
# make version to update the version number from .git commit
RUN cd /var/webModules && ./mkversion.sh

#######
#
# --- oc.nginx image start here ---
#
FROM abcdesktopio/oc.nginx:3.2
# COPY updated files from builder container to oc.nginx
COPY --from=builder var/webModules /var/webModules
RUN cat /var/webModules/index.html
