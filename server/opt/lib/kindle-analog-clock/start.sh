#!/bin/sh

IP='192.168.2.2'

cd "$(dirname "$0")"

if [ $(uname -n) == "kindle" ]; then
	/usr/sbin/eips -c
else
    ssh root@${IP} "/usr/sbin/eips -c"
fi

./audio_server.py >/tmp/kindle-analog-clock-audio-server_start.out 2>&1 &
./clock.py >/tmp/kindle-analog-clock_start.out 2>&1 &

exit 0
