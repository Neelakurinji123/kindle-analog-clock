#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Update     : 31 May 2024

import json, random, socket
import time as t
from datetime import datetime
from multiprocessing import Process
from KindleAudio import KindleMusic

def play(c):
    c_music = c['music']
    c_env = c['env']
    now = datetime.now().timestamp()
    year, mon, mday, hr, mi, sec, _, _, _ = datetime.now().timetuple()
    s = [ list(x.items())[0][0] for x in c_music.values()]
    p = [ list(x.items())[0] for x in c_music.values()]
    for n in p:
        if n[0] == 'True':
            entry = n[1]
            [start_hr, start_mi] = list(map(int, entry['start_time'].split(':')))
            [stop_hr, stop_mi] = list(map(int, entry['stop_time'].split(':')))
            start_dt = datetime(year, mon, mday, start_hr, start_mi).timestamp()
            stop_dt = datetime(year, mon, mday, stop_hr, stop_mi).timestamp()
#            if start_dt == stop_dt or (start_dt >= now and stop_dt <= now):
            if start_dt <= now <= stop_dt:
                print('config: ', entry)
                song_list = KindleMusic(song_list=None, **entry).get_playlist()
                player = KindleMusic(song_list=song_list, **entry)
                proc = Process(target=player.play(), args=())
                proc.start()
            else:
                pass  

if __name__ == "__main__":
    setting ='music.json'
    with open(setting, 'r') as f:
        c = json.load(f)
    f.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    play(c)
