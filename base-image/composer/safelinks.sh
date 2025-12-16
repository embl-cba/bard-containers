#!/bin/bash
# this script look for links files
for filename in $(find . -type l);
do
  if realpath $filename | grep -E "^$PWD" > /dev/null
  then
    true
    # echo '.'
    # echo 'this file is safe'
  else
    echo "this file links externally $filename"
    realpathname=$(realpath "$filename")
    echo "realpathname=$realpathname"
    echo "rm $filename"
    rm "$filename"
    echo "cp $realpathname $filename"
    cp "$realpathname" "$filename"
  fi
done
