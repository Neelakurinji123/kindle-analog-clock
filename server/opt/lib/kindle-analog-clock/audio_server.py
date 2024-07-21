#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Update     : 31 May 2024

import json, random, socket, os, signal, sys
from pathlib import Path
import time as t
from datetime import datetime
from multiprocessing import Process
import socketserver


# Working dir
this_file = os.path.realpath(__file__)
path = Path(this_file).parents[0]
os.chdir(str(path))

from KindleAudio import KindleMusic, KindleAlarm

def www():
    with open('/tmp/kindle-analog-clock-www-server.pid', 'w') as f:
        f.write(str(os.getpid()))
    f.close()
    from http.server import HTTPServer
    from http.server import SimpleHTTPRequestHandler
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

def music_play(c, c_music, queue):
    num = queue[1]
    a = c_music[str(num)]
    timeout = int(float(queue[2])) if len(queue) >= 3 else -1
    entry = list(a.values())[0] # dict()
    song_list = KindleMusic(c=c, song_list=None, **entry).get_playlist()
    player = KindleMusic(c=c, song_list=song_list, timeout=timeout, **entry)
    proc_music = Process(target=player.play(), args=())
    proc_music.start()

def alarm_play(c, c_alarm, queue):
    num = queue[1]
    a = c_alarm[str(num)]
    entry = list(a.values())[0]
    alarm = KindleAlarm(c=c, **entry)
    proc_alarm = Process(target=alarm.play(), alarm_args=())
    proc_alarm.start()

def main(c, c_music, c_alarm):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    class MyTCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            self.data = self.request.recv(1024).strip()
            m = self.data.decode()
            queue = m.split('#')
            if queue[0] == 'music':
                music_play(c, c_music, queue)
            elif queue[0] == 'alarm':
                alarm_play(c, c_alarm, queue)
            elif m == 'terminate':
                sys.exit()
        
    HOST, PORT = "localhost", 8001
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()  

if __name__ == "__main__":
    setting ='setting.json'
    with open(setting, 'r') as f:
        c = json.load(f)['clock']
    f.close()
    setting ='music.json'
    with open(setting, 'r') as f:
        c_music = json.load(f)['music']
    f.close()
    setting ='alarm.json'
    with open(setting, 'r') as f:
        c_alarm = json.load(f)['alarm']
    f.close()
    if c['kindle_server'] == False:
        try:
            webserver = Process(target=www, args=())
            webserver.start()  
        except Exception as e:
            print(e)

    with open('/tmp/kindle-analog-clock-audio-server.pid', 'w') as f:
        f.write(str(os.getpid()))
    f.close()
    main(c, c_music, c_alarm)
