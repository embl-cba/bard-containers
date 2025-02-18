#!/bin/bash

export STDOUT_LOGFILE=/tmp/lastcmd.log
export STDOUT_ENVLOGFILE=/tmp/lastcmdenv.log
START_TIME=$(date +%s)

log() {
echo "$(date) $1" >> $STDOUT_LOGFILE
}


# Dump env APP ARG and APPARG to log file
# export VAR
log "start new application $APP"
log "-> APP=$APP"
log "-> ARGS=$ARGS"
log "-> APPARGS=$APPARGS"
log "-> id=$(id)"

env > $STDOUT_ENVLOGFILE
INIT_OVERLAY_PATH=/composer/init.overlay.d

log "run init overlay scripts"
# Run init overlay script file if exist
if [ -d "$INIT_OVERLAY_PATH" ]; then
	for overlay_script in "INIT_OVERLAY_PATH/*.sh"
	do
		if [ -f $overlay_script -a -x $overlay_script ]; then
			log "running $overlay_script"
			$overlay_script >> $STDOUT_LOGFILE
		fi
	done
fi
log "init overlay scripts done" 

# Run init APP if exist
BASENAME_APP=$(basename "$APP")
log "BASENAME_APP=$BASENAME_APP"
SOURCEAPP_FILE=/composer/init.d/init.${BASENAME_APP}
if [ -f "$SOURCEAPP_FILE" ]; then
	log "run $SOURCEAPP_FILE"
	$SOURCEAPP_FILE "$APPARGS" > /tmp/${BASENAME_APP}.cmd.log 2>&1
	log "done  $SOURCEAPP_FILE"
fi

if [ ! -d ~/.cache ]; then
     mkdir  ~/.cache
fi

if [ -d /composer/.cache ]; then
	cp -nr /composer/.cache/* ~/.cache/
fi 

# .Xauthority
if [ ! -f ~/.Xauthority ]; then
	log "~/.Xauthority does not exist"
	ls -la ~ >> $STDOUT_LOGFILE
	# create a MIT-MAGIC-COOKIE-1 entry in .Xauthority
	if [ ! -z "$XAUTH_KEY" ]; then
        	log "xauth add $DISPLAY MIT-MAGIC-COOKIE-1 $XAUTH_KEY"
        	xauth add $DISPLAY MIT-MAGIC-COOKIE-1 $XAUTH_KEY >> $STDOUT_LOGFILE 2>&1
		log "xauth add done exitcode=$?"
	fi
else
	log "~/.Xauthority exists"
fi

# create a PULSEAUDIO COOKIE 
if [ ! -z "$PULSEAUDIO_COOKIE" ]; then
	log "setting pulseaudio cookie"
	if [ ! -f ~/.config/pulse/cookie ]; then
		echo 'create ~/.config/pulse/cookie'
                mkdir -p ~/.config/pulse
		# create a 256 Bytes cookie file for pulseaudio
                for i in {1..8} 
		do 
  			echo -n "$PULSEAUDIO_COOKIE" >> ~/.config/pulse/cookie
     		done
        fi
fi

# start dbux-launch if exists
if [ -x /usr/bin/dbus-launch ]; then
	rm -f /var/lib/dbus/machine-id
 	dbus-uuidgen --ensure=/var/lib/dbus/machine-id
	mkdir -p /run/user/$(id -u)/dconf
        export $(/usr/bin/dbus-launch)
	log "dbus-launch done exitcode=$?" 
fi
log "end of init"

log "start nvidia settings"
if [ -d /proc/driver/nvidia ]; then
 	if [ -x /usr/bin/nvidia-smi ]; then
        # command line /usr/bin/nvidia-smi found
        # nvidia-smi read gpu_uuid
	    uuid=$(nvidia-smi -L | grep "UUID: MIG" | grep -oP '(?<=UUID: ).*?(?=\))')
		if [ -z "$uuid" ]; then
			gpu_uuid=$(nvidia-smi --query-gpu=gpu_uuid --format=csv,noheader)
   		else
     		gpu_uuid=$uuid
		fi
           	NVIDIA_GPU="{ \"NVIDIA_VISIBLE_DEVICES\" : \"$gpu_uuid\" }"  
    fi
fi

echo NVIDIA_VISIBLE_DEVICES=$NVIDIA_VISIBLE_DEVICES
log "end of nvidia settings"

# change current dir to homedir 
# to fix ntlm_auth load for firefox on alpine distribution
# firefox does not support SSO, does not execute ntlm_auth if ntlm_auth not in current dir or in $PATH
cd ~
log "current dir is $(pwd)"
log "running $APP at $(date)"

# Run the APP with args
if [ -z "$ARGS" ]; then    
	if [ -z "$APPARGS" ]; then  
		# $APPARGS is empty or unset 
		# $ARGS is empty or unset
		# no params
		"${APP}" 2>&1 | tee /tmp/$BASENAME_APP.log 
	else
		# $APPARGS is set 
                # $ARGS is empty or unset
                # APPARGS is the only param
		"${APP}" "${APPARGS}" 2>&1 | tee /tmp/$BASENAME_APP.log
	fi
else
	if [ -z "$APPARGS" ]; then  
                # $APPARGS is empty or unset 
                # $ARGS is set
                # $ARGS is the only param
                "${APP}" ${ARGS} 2>&1 | tee /tmp/$BASENAME_APP.log
        else
		# $APPARGS is set 
                # $ARGS is set
                # use params: $ARGS and $APPARGS
                "${APP}" ${ARGS} "${APPARGS}" 2>&1 | tee /tmp/$BASENAME_APP.log
        fi
fi

EXIT_CODE=$?
# log the exit code in /tmp/lastcmd.log
log "end of app exit_code=$EXIT_CODE"


# exit with the application exit code 
exit $EXIT_CODE

