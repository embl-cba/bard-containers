#!/bin/bash

NAMESPACE="abcdesktop-ns"
TIME_THRESHOLD_SECONDS=172800 #48 hrs
EXCLUDE_PREFIXES=("memcached-od" "mongodb-od" "nginx-od" "openldap-od" "pyos-od" "speedtest-od" "cleanup" "filebrowser")

CURRENT_TIME=$(date -d now +%s)
echo "DEBUG: Current time in epoch seconds: $CURRENT_TIME"

kubectl get pods -n $NAMESPACE --field-selector=status.phase=Running -o jsonpath='{range .items[*]}{.metadata.name} {.status.startTime}{"\n"}{end}' | while read -r line; do
  POD_NAME=$(echo $line | awk '{print $1}')
  START_TIME=$(echo $line | awk '{print $2}')


  SKIP=false
  for prefix in "${EXCLUDE_PREFIXES[@]}"; do
    if [[ $POD_NAME == $prefix* ]]; then
      echo "Skipping pod $POD_NAME as it is a system pod $prefix"
      SKIP=true
      break
    fi
  done

  if [ "$SKIP" = true ]; then
    continue
  fi
  
  START_SECONDS=$(date -d "$START_TIME" +%s)

  RUNNING_HOURS=$((CURRENT_TIME - START_SECONDS ))

  echo "DEBUG: pod $POD_NAME start time in ephoch seconds: $START_SECONDS, has been running for $RUNNING_HOURS seconds"

  if [ "$RUNNING_HOURS" -ge "$TIME_THRESHOLD_SECONDS" ]; then
    echo "DEBUG: Deleting pod $POD_NAME, has been running for $RUNNING_HOURS seconds. Start time: $START_SECONDS"
    kubectl delete pod "$POD_NAME" -n $NAMESPACE
  fi
done
