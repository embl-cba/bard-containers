#!/bin/bash
set -e

CONFIG_DIR="${HOME}/.globusonline"
SETUP_KEY_FILE="${HOME}/.globusonline/setup-key.txt"
RESTRICT_FILE="${HOME}/.globusonline/restrict.txt"
mkdir -p "${CONFIG_DIR}"

if [ ! -f "${CONFIG_DIR}/personal.json" ]; then
  echo "-----------------------------------------"
  echo "Globus Connect Personal setup"
  echo "-----------------------------------------"
  if [ -f "$SETUP_KEY_FILE" ]; then
        echo "[INFO] Found setup key file: $SETUP_KEY_FILE"
        SETUP_KEY=$(cat "$SETUP_KEY_FILE" | tr -d '[:space:]')
        /opt/globusconnectpersonal-3.2.8/globusconnectpersonal -setup "$SETUP_KEY"
  else
	echo "[INFO] No setup key supplied."
        echo "[INFO] Launching Globus Connect Personal UI for manual login..."
	/opt/globusconnectpersonal-3.2.8/globusconnectpersonal -gui &
	GCP_PID=$!
        wait $GCP_PID
        exit 0
  fi
fi

if [ -f "$RESTRICT_FILE" ]; then
    exec /opt/globusconnectpersonal-3.2.8/globusconnectpersonal -start -restrict-paths "$RESTRICT_FILE"
else
    echo "[WARN] No restriction file found — exposing entire home directory!"
    exec  /opt/globusconnectpersonal-3.2.8/globusconnectpersonal -start 
fi
