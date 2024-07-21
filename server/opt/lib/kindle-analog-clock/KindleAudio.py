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
    def __init__(self, c, song_list=None, timeout=-1, **entry):
        self.playlist = entry.get('playlist')
        self.playmode = entry.get('playmode')
        self.repeat = entry.get('repeat')
        self.location = entry.get('file_location')
        self.timeout = int(timeout)
        self.song_list = song_list
        self.start = int(t.time())
        self.kindleIP = '192.168.2.2'
        self.serverIP = '192.168.2.1'
        self.kindle_server = c.get('kindle_server')

    def play(self):
        log = '/tmp/kindle-analog-clock_music.log'
        
        def reset_mplayer():
            if self.kindle_server == False:
                cmd = f'ssh root@{self.kindleIP} \"kill `pidof mplayer`\"'
            else:
                cmd = 'kill `pidof mplayer`'
            proc = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()

        if self.location == 'server' and self.kindle_server == False:
            for n in self.song_list:
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
                    cmd = f'ssh root@{self.kindleIP} \"/mnt/us/mplayer/mplayer http://{self.serverIP}:8000/\'{n}\'\" | tee {log}'
                    proc = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()
        elif self.location == 'kindle':
            print('test123', self.song_list)
            for n in self.song_list:
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
                    if self.kindle_server == True:
                        cmd =  f'/mnt/us/mplayer/mplayer \'{n}\' | tee {log}'
                    else:
                        cmd =  f'ssh root@{self.kindleIP} \"/mnt/us/mplayer/mplayer \'{n}\'\" | tee {log}'
                    proc = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()
        else:
            raise ValueError("To run on kindle server, music files have to be located at the local storage.")

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
        if self.location == 'server' and self.kindle_server == False:
            cmd = f'find music/\"{self.playlist}\" -maxdepth 1 -name *.m4a -o -name *.mp3'
            r = check_output([cmd], shell=True)
            song_list = r.decode().split('\n')
            if self.playmode == 'normal':
                pass
            elif self.playmode == 'reverse':
                song_list.reverse()
            elif self.playmode == 'shuffle':
                random.shuffle(song_list)
        elif self.location == 'kindle':
            if self.kindle_server == True:
                cmd =  f'find /mnt/us/audible/\"{self.playlist}\" -maxdepth 1 -name *.m4a -o -name *.mp3'
            else:
                cmd =  f'ssh root@{self.kindleIP} \"find /mnt/us/audible/\\\"{self.playlist}\\\" -maxdepth 1 -name *.m4a -o -name *.mp3\"'
            r = check_output([cmd], shell=True)
            song_list = r.decode().split('\n')
            if self.playmode == 'normal':
                pass
            elif self.playmode == 'reverse':
                song_list.reverse()
            elif self.playmode == 'shuffle':
                random.shuffle(song_list)
        else:
            raise ValueError("To run on kindle server, music files have to be located at the local storage.")
        return song_list

class KindleAlarm:
    def __init__(self, c, **entry):
        self.timeout = int(re.sub(r'm$', '', entry.get('timeout'))) * 60
        self.sound = entry.get('sound')
        self.kindleIP = '192.168.2.2'
        self.serverIP = '192.168.2.1'
        self.kindle_server = c.get('kindle_server')

    def play(self):
        now = int(t.time())
        try:
            if self.kindle_server == True:
                cmd = f'aplay sounds/{self.sound}'
            else:
                cmd = f'ssh root@{self.kindleIP} \"curl http://{self.serverIP}:8000/sounds/{self.sound} | aplay\"'
            while t.time() < now + self.timeout:
                process1 = Popen([cmd], shell=True, stdout=DEVNULL, stderr=STDOUT).wait()
        except Exception as e:
            print(e)
            exit(1)
        
        
     
