#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Update     : 31 May 2024

import random, re, os
import time as t
from subprocess import Popen, check_output, DEVNULL, STDOUT, run

with open('/tmp/kindle-analog-clock-KindleAudio.pid', 'w') as f:
    f.write(str(os.getpid()))
f.close()

class KindleMusic:
    def __init__(self, song_list=None, timeout=-1, **entry):
        self.playlist = entry.get('playlist')
        self.playmode = entry.get('playmode')
        self.repeat = entry.get('repeat')
        self.location = entry.get('file_location')
        self.timeout = int(timeout)
        self.song_list = song_list
        self.start = int(t.time())

    def play(self):
        location = self.location
        song_list = self.song_list
        log = '/tmp/kindle-analog-clock_music.log'
        
        def reset_mplayer():
            cmd = f'ssh root@192.168.2.2 \"kill `pidof mplayer`\"'
            proc = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()

        if location == 'server':
            for n in song_list:
                if not self.timeout == -1 and self.timeout < int(t.time()) - self.start:
                    try:
                        reset_mplayer()
                        exit(0)
                    except Exception as e:
                        print(e)
                        exit(1) 
                else:
                    reset_mplayer()
                    # Save music file name
                    with open('/tmp/kindle-analog-clock-KindleAudio_file', 'w') as f:
                        f.write(n)
                    f.close()
                    cmd = f'ssh root@192.168.2.2 \"/mnt/us/mplayer/mplayer http://192.168.2.1:8000/\'{n}\'\" | tee {log}'
                    proc = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()
        elif location == 'kindle':
            for n in song_list:
                if not self.timeout == -1 and self.timeout < int(t.time()) - self.start:
                    try:
                        reset_mplayer()
                        exit(0)
                    except Exception as e:
                        print(e)
                        exit(1)
                else:
                    reset_mplayer()
                    # Save music file name
                    with open('/tmp/kindle-analog-clock-KindleAudio_file', 'w') as f:
                        f.write(n)
                    f.close()
                    cmd =  f'ssh root@192.168.2.2 \"/mnt/us/mplayer/mplayer \'{n}\'\" | tee {log}'
                    proc = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()

        if self.repeat == 'True':
            #reset_mplayer()
            self.song_list = self.get_playlist()
            self.play()
        else:
            try:
                reset_mplayer()
                exit(0)
            except Exception as e:
                print(e)
                exit(1)

    def get_playlist(self):
        playmode = self.playmode
        repeat = self.repeat
        location = self.location
        playlist = self.playlist
        if location == 'server':
            cmd = f'find music/\\"{playlist}\\" -maxdepth 1 -name *.m4a -o -name *.mp3'
            r = check_output([cmd], shell=True)
            song_list = r.decode().split('\n')
            print('test123', song_list)
            if playmode == 'normal':
                pass
            elif playmode == 'reverse':
                song_list.reverse()
            elif playmode == 'shuffle':
                random.shuffle(song_list)
        elif location == 'kindle':
            cmd =  f'ssh root@192.168.2.2 \"find /mnt/us/audible/\\"{playlist}\\" -maxdepth 1 -name *.m4a -o -name *.mp3\"'
            r = check_output([cmd], shell=True)
            song_list = r.decode().split('\n')
            if playmode == 'normal':
                pass
            elif playmode == 'reverse':
                song_list.reverse()
            elif playmode == 'shuffle':
                random.shuffle(song_list)
        return song_list

class KindleAlarm:
    def __init__(self, **entry):
        self.timeout = int(re.sub(r'm$', '', entry.get('timeout'))) * 60
        self.sound = entry.get('sound')

    def play(self):
        now = int(t.time())
        try:
            cmd = f'ssh root@192.168.2.2 \"curl http://192.168.2.1:8000/sounds/{self.sound} | aplay\"'
            while t.time() < now + self.timeout:
                process1 = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()
        except Exception as e:
            print(e)
            exit(1)
        
        
     
