#!/bin/bash

if [ $1 = "start" ]
then
#   python3 autosub.py > autosub.log & 
   if [ -z "$2" ]
   then
      python3 autosub.py & 
      echo $! > autosub.pid
   else
      python3 autosub.py --config-file $2 & 
      echo $! > autosub.pid
   fi
elif [ $1 = "stop" ]
then
   PID=$(cat autosub.pid)
   kill -30 $PID
   rm autosub.pid
else
   echo "Usage: ./autosub.sh [start|stop]"
fi
