#
# --- update oc.nginx:builder image start here ---
# use the abcdesktopio/oc.nginx:builder
# oc.nginx:builder contains Makefile and tools like nodejs, lessc need to update the ui.json file
# oc.nginx:builder source https://raw.githubusercontent.com/abcdesktopio/oc.nginx/main/Dockerfile.builder          
#######
FROM abcdesktopio/oc.nginx:builder as builder


# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && node -v \
    && npm -v
    
RUN git clone https://git.embl.org/grp-cbbcs/webModules.git /var/webModules

RUN cd /var/webModules && make install
RUN cd /var/webModules && make updatejs
RUN cd /var/webModules && make dev 
RUN cd /var/webModules && ./mkversion.sh

#######
# --- oc.nginx image start here ---
#
FROM abcdesktopio/oc.nginx:3.4
COPY --from=builder var/webModules /usr/share/nginx/html