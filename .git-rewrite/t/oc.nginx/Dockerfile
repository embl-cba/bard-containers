FROM abcdesktopio/oc.nginx:builder as builder

# copy data files
COPY --from=abcdesktopio/oc.nginx:3.0 var/webModules /var/webModules
# copy updated file ui.json 
COPY ui.json /var/webModules/transpile/config/
COPY index.mustache.html /var/webModules/
COPY eubi.png /var/webModules/img/
COPY eosc-logo.png /var/webModules/img/

# run makefile 
RUN cd /var/webModules && make prod

# --- START Build image ---
FROM abcdesktopio/oc.nginx:3.0

# COPY generated web site from builder container
COPY --from=builder var/webModules /var/webModules
RUN cat /var/webModules/index.html

LABEL name="frontend abcdesktop@embl base image" \
      maintainer="abcdesktop" \
      version="3.0"

# end of nginx update
