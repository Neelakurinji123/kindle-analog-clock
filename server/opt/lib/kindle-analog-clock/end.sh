#!/bin/sh

cd "$(dirname "$0")"

sleep 3   # deley 3 secs

kill $(cat /tmp/kindle-analog-clock.pid)
kill $(cat /tmp/kindle-analog-clock-audio-server.pid)

if [ "$(uname -n)" == "kindle" ]; then
	kill $(cat /tmp/kindle-analog-clock-www-server.pid)
fi

exit 0
