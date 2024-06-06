import os
import time as t
import re
import subprocess

log='/tmp/kindle-analog-clock_music.log'

while True:
    song_time = subprocess.check_output(["cat", log])
    a = song_time.decode().split()
    title, artist, album, progress, song_time = str(), str(), str(), int(0), [0, 0]

    try:
        title_location = [i for i, item in enumerate(a) if re.match('title:', item)]
        artist_location = [i for i, item in enumerate(a) if re.match('artist:', item)]
        album_location = [i for i, item in enumerate(a) if re.match('album:', item)]
        end_location = [i for i, item in enumerate(a) if re.match('===', item)]
        title = ' '.join(a[title_location[0]:artist_location[0]])
        artist = ' '.join(a[artist_location[0]:album_location[0]])
        album = ' '.join(a[album_location[0]:end_location[0]])
        progress = int(float(a[-7]) / float(a[-4]) * 100)
        song_time = [str(int(float(a[-7]) / 60)), str(int(float(a[-7]) % 60))]
        print('title     :', title)
        print('artist    :', artist)
        print('album     :', album)
        print('song time :', ':'.join(song_time))
        print('progress  :', a[-7], a[-4], progress )

    except Exception as e:
        print(e)

    t.sleep(2)

