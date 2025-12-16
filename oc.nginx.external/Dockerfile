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

RUN cd /var/webModules && make install
RUN cd /var/webModules && make updatejs
RUN cd /var/webModules && make dev 
RUN cd /var/webModules && ./mkversion.sh
######
#
# --- oc.nginx image start here ---
#
FROM abcdesktopio/oc.nginx:3.4
# COPY updated files from builder container to oc.nginx
COPY --from=builder var/webModules /usr/share/nginx/html