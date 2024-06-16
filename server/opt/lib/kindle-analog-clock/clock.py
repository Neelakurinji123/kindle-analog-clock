#!/usr/bin/env python3
# encoding=utf-8
# -*- coding: utf-8 -*-

# Written by : krishna@hottunalabs.net
# Update     : 31 May 2024 

import json, os, sys, re, io, math, socket
from codecs import encode
from pathlib import Path
import time as t
from datetime import datetime
import zoneinfo
from wand.image import Image
from wand.display import display
from cairosvg import svg2png
from multiprocessing import Process
from subprocess import Popen, check_output, DEVNULL, STDOUT, PIPE

# Working dir
this_file = os.path.realpath(__file__)
path = Path(this_file).parents[0]
os.chdir(str(path))

kindleIP = '192.168.2.2'

import SVGtools

def send_message(m):
    HOST, PORT = "localhost", 8001
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(bytes(m + "\n", "utf-8"))
    sock.close()

def wordwrap(text, length):
    if len(text) >= length:
        w = text[0:(length - 2)] + '..'
    else:
        w = text
    return w

def reset_display():
    cmd = f'ssh root@{kindleIP} \"cd /tmp; /usr/sbin/eips -c\"'
    proc = Popen([cmd],shell=True, stdout=PIPE, stderr=PIPE)

def load_icon(x, y, name, scale=3.0, mirror=False):
    path = 'images/'
    icon = path + name
    with open(icon, 'r') as f:
        a = f.read()
    f.close()
    if mirror == True:
        b = SVGtools.transform(f'({-scale},0,0,{scale},{x},{y})', a).svg()
    else:
        b = SVGtools.transform(f'({scale},0,0,{scale},{x},{y})', a).svg()
    return b

def create_svg(c, _svg):
    #layout = 'landscape'
    #w, h = (800, 600) if layout == 'landscape' else (600, 800)
    w, h = 800, 600
    encoding = c['encoding']
    svg = f'''<?xml version="1.0" encoding="{encoding}"?>
<svg xmlns="http://www.w3.org/2000/svg" height="{h}" width="{w}" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink">'''
    svg += '\n'
    svg += _svg
    #svg += '<g font-family="' + 'Droid Sans' + '">\n'
    svg += '\n</svg>'
    return svg

class DrawClock:
    def __init__(self, **kw2):
        self.w = kw2.get('w')
        self.h = kw2.get('h')
        self.radiusX = kw2.get('radiusX')
        self.radiusY = kw2.get('radiusY')
        self.innerRadiusX = kw2.get('innerRadiusX')
        self.innerRadiusY = kw2.get('innerRadiusY')
        self.v = kw2.get('v')
        self.step = kw2.get('step')
        self.rotate = ( self.v * 360 / self.step ) - 90
        self.color = kw2.get('color')
        
    def svg(self):
        v = self.v
        step = self.step
        if v == 0:
            v1 = step * 0.5
            v2 = step * 0.5
            self.v = v1
            self.rotate = (v1 * 360 / step) - 90
            a = self.draw()
            self.v = v2
            self.rotate = (v2 * 360 / step) + 90
            a += self.draw()
        elif (v * 360 / step) > 180:
            v1 = step * 0.5
            v2 = v - v1
            self.v = v1
            self.rotate = (v1 * 360 / step) - 90
            a = self.draw()
            self.v = v2
            self.rotate = (v2 * 360 / step) + 90
            a += self.draw()
        else:
            a = self.draw()
        return a
            
    def draw(self):
        pi, cos, sin = math.pi, math.cos, math.sin
        v, step = self.v, self.step
        w, h = self.w, self.h
        ang = 180 / (v * 360 / step) 
        rotate = self.rotate
        centerX = self.w * 0.5
        centerY = self.h * 0.5
        radiusX = self.radiusX
        radiusY = self.radiusY
        startX = centerX + radiusX
        startY = centerY
        radiusEndX = centerX + cos(pi / ang) * radiusX
        radiusEndY = centerY - sin(pi / ang) * radiusY
        endX = startX - radiusX
        endY = startY
        innerRadiusX = self.innerRadiusX
        innerRadiusY = self.innerRadiusY
        innerStartX = centerX + innerRadiusX
        innerStartY = centerY
        innerRadiusEndX = centerX + cos(pi / ang) * innerRadiusX
        innerRadiusEndY = centerY - sin(pi / ang) * innerRadiusY
        innerEndX = innerStartX - innerRadiusX
        innerEndY = innerStartY
        color = self.color
        a = f'''<path d="M {startX} {startY}
A {radiusX} {radiusY}, 0, 0, 0, {radiusEndX} {radiusEndY}
L {innerRadiusEndX} {innerRadiusEndY}
A {innerRadiusX} {innerRadiusY}, 0, 0, 1, {innerStartX} {innerStartY}
Z" fill="{color}" transform="rotate({rotate}, {centerX}, {centerY})"/>
'''    
        return a

def alarm(c, c_alarm, hr, mi, sec):
    alarm_svg = str()
    alarm_run = None
    interval = int(c['set_interval'])
    s = [list(x.items())[0][0] for x in c_alarm.values()]
    p = [list(x.items())[0] for x in c_alarm.values()]
    for i, n in enumerate(p, 1):
        if n[0] == 'True':
            entry = n[1]
            year, mon, mday, _, _, _, _, _, _ = datetime.now().timetuple()
            now = int(datetime(year, mon, mday, hr, mi, sec).timestamp())
            [start_hr, start_mi] = list(map(int, entry['time'].split(':')))
            start_dt = int(datetime(year, mon, mday, start_hr, start_mi).timestamp())
            timeout = int(re.sub(r'm$', '', entry['timeout']))
            stop_dt = start_dt + timeout * 60
            if start_dt == now:
                alarm_run = True
                name = 'bell_ringing_2.svg'
                x, y = 350, 250
                alarm_svg = load_icon(x=x, y=y, name=name, scale=4.0)
                try:
                    send_message('alarm#{}'.format(i))
                except Exception as e:
                    print(e)
                return alarm_svg, alarm_run
            elif start_dt <= now <= stop_dt and ((now - start_dt) / interval) % 2 == 1:
                alarm_run = True
                name = 'bell_ringing_2.svg'
                x, y = 450, 250
                alarm_svg = load_icon(x=x, y=y, name=name, scale=4.0, mirror=True)
                return alarm_svg, alarm_run
            elif start_dt <= now <= stop_dt:
                alarm_run = True
                name = 'bell_ringing_2.svg'
                x, y = 350, 250
                alarm_svg = load_icon(x=x, y=y, name=name, scale=4.0)
                return alarm_svg, alarm_run
            elif now == stop_dt:
                alarm_run = True
                name = 'bell_ringing_2.svg'
                x, y = 0, 5          
                alarm_svg = load_icon(x=x, y=y, name=name, scale=4.0)
                return alarm_svg, alarm_run
            else:
                alarm_run = False
                name = 'bell.svg'
                x, y = 0, 5          
                alarm_svg = load_icon(x=x, y=y, name=name)
    return alarm_svg, alarm_run



def music(c, w, h, c_music, hr, mi, sec):
    music_svg = str()
    env = c_music['env']
    music = c_music['music']
    music_run = None
    year, mon, mday, _, _, _, _, _, _ = datetime.now().timetuple()
    now = datetime(year, mon, mday, hr, mi, sec).timestamp()
    s = [ list(x.items())[0][0] for x in music.values()]
    p = [ list(x.items())[0] for x in music.values()]

    def get_song_info(entry):
        log = '/tmp/kindle-analog-clock_music.log'

        try:
            song_log = check_output(["cat", log])
            a = song_log.decode().split()
        except Exception as e:
            print(e)
            
        try:
            with open('/tmp/kindle-analog-clock-KindleAudio_file', 'r') as f:
                b1 = f.read()
                b2 = Path(b1).name
                file_name = re.sub(r'.mp3$|m4a$', '', b2)
            f.close()
        except Exception as e:
            print(e)
            file_name = str()

        title, artist, album, progress, song_time = str(), str(), str(), int(0), ['00', '00']
        try:
            title_location = [i for i, item in enumerate(a) if re.match('title:', item)]
            artist_location = [i for i, item in enumerate(a) if re.match('artist:', item)]
            album_location = [i for i, item in enumerate(a) if re.match('album:', item)]
            end_location = [i for i, item in enumerate(a) if re.match('===', item)]
            title = ' '.join(a[title_location[0]:artist_location[0]]) if not title_location == list() and not artist_location == list() else 'n/a'
            artist = ' '.join(a[artist_location[0]:album_location[0]]) if not artist_location == list() and not album_location == list() else 'n/a'
            album = ' '.join(a[album_location[0]:end_location[0]]) if not album_location == list() and not end_location == list() else 'n/a'

            # Fix encoding errors
            def fix_encode(n):
                #out = encode(n, encoding='latin_1', errors='replace')
                #n = out.decode('latin_1')
                n = re.sub(r'&', '&amp;', n)
                return n
                
            title = fix_encode(title)
            artist = fix_encode(artist)
            album = fix_encode(album)
            if entry['file_location'] == 'server':
                progress = int(float(a[-7]) / float(a[-4]) * 100)
                song_time = [str(f'{int(float(a[-7]) / 60):02d}'), str(f'{int(float(a[-7]) % 60):02d}')]
            elif entry['file_location'] == 'kindle':
                progress = int(float(a[-6]) / float(a[-3]) * 100)
                song_time = [str(f'{int(float(a[-6]) / 60):02d}'), str(f'{int(float(a[-6]) % 60):02d}')]
            title = re.sub(r'^title: ', '', title)
            title = file_name if title == 'n/a' and entry['file_location'] == 'server' else title
            artist = re.sub(r'^artist: ', '', artist)
            album = re.sub(r'^album: ', '', album)
        except TypeError:
                progress = 0
                song_time = ['00', '00']
        except Exception as e:
            print(e)
        return title, artist, album, progress, song_time
    
    def create_music_svg(w, h, env, title, artist, album, progress, song_time, *args):
        if env['display'] == 'circle':
            name = 'speaker.svg'
            x, y = 358, 257
            svg = load_icon(x=x, y=y, name=name, scale=5.4)
            kw2 = {'w': w, 'h': h, 'radiusX': c['stroke_music_radius'], 'radiusY': c['stroke_music_radius'],
                    'innerRadiusX': c['stroke_music_inner_radius'], 'innerRadiusY': c['stroke_music_inner_radius'],
                    'v': progress, 'step': 99, 'color': c['color_music']}
            progress_circle = DrawClock(**kw2)
            svg += progress_circle.svg()
            x, y = 25, 575
            font_size = 25
            length = 35
            svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=wordwrap(title, length)).svg()
            #y += 30
            #svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=wordwrap(artist, length), stroke='rgb(128,128,128)').svg()
            #y += 30
            #svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=wordwrap(album, length), stroke='rgb(128,128,128)').svg()
            x, y = 785, 55
            font_size = 45
            svg += SVGtools.text(anchor='end', fontsize=font_size, x=x, y=y, v=':'.join(song_time), stroke='rgb(128,128,128)').svg()
        elif env['display'] == 'bar':
            name = 'speaker.svg'
            x, y = 358, 257
            svg = load_icon(x=x, y=y, name=name, scale=5.4)
            style = 'stroke:rgb(128,128,128);stroke-width:20px;'
            svg += SVGtools.line(x1=0, x2=(progress / 99 * 800), y1=600, y2=600, style=style).svg()
            x, y = 25, 585
            font_size = 25
            length = 40
            svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=wordwrap(title, length)).svg()
            #y += 30
            #svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=wordwrap(artist, length), stroke='rgb(128,128,128)').svg()
            #y += 30
            #svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=wordwrap(album, length), stroke='rgb(128,128,128)').svg()
            x, y = 25, 530
            #x, y = 785, 55
            font_size = 45
            svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v=':'.join(song_time), stroke='rgb(128,128,128)').svg()
            #svg += SVGtools.text(anchor='end', fontsize=font_size, x=x, y=y, v=':'.join(song_time), stroke='rgb(128,128,128)').svg()
        return svg
    
    for i, n in enumerate(p, 1):
        if n[0] == 'True':
            entry = n[1]
            [start_hr, start_mi] = list(map(int, entry['start_time'].split(':')))
            [stop_hr, stop_mi] = list(map(int, entry['stop_time'].split(':')))
            start_dt = datetime(year, mon, mday, start_hr, start_mi).timestamp()
            stop_dt = datetime(year, mon, mday, stop_hr, stop_mi).timestamp()
            timeout = str(int(stop_dt - start_dt))
            if int(start_dt) == int(now):
                try:
                    send_message(f'music#{i}#{timeout}')
                except Exception as e:
                    print(e)
                music_run = True
                args = get_song_info(entry)
                music_svg = create_music_svg(w, h, env, *args)
                return music_svg, music_run
            elif int(start_dt) <= int(now) <= int(stop_dt):
                music_run = True
                args = get_song_info(entry)
                music_svg = create_music_svg(w, h, env, *args)
                return music_svg, music_run
            else:
                music_run = False
                name = 'queue_music.svg'
                x, y = 0, 530          
                music_svg = load_icon(x=x, y=y, name=name)

    return music_svg, music_run

def schedule(c_schedule, hr, mi, sec):
    schedule_svg = str()
    task_run = None
    s = [ list(x.items())[0][0] for x in c_schedule.values()]
    year, mon, mday, _, _, _, _, _, _ = datetime.now().timetuple()
    now = datetime(year, mon, mday, hr, mi, sec).timestamp()

    def message(title, items):
        x, y = 400, 150
        font_size = 60
        svg = str()
        svg = SVGtools.text(anchor='middle', fontsize=font_size, x=x, y=y, v=title).svg()
        x, y = 175, 240
        font_size = 35
        for key, value in items.items():
            svg += SVGtools.text(anchor='start', fontsize=font_size, x=x, y=y, v='* ' + value).svg()
            y += 50
        return svg

    def schedule_icon(v):
        name = 'task_done.svg'
        x, y = 13, 270
        svg = str()
        svg = load_icon(x=x, y=y, name=name)
        return svg

    if "True" in s:
        for d in c_schedule.values():
            b, v = list(d.items())[0]
            title = v['task']['title']
            items = v['task']['items']
            if b == 'True':
                sch_hr, sch_mi = v['time'].split(':')
                valid = int(re.sub(r'm$', '', v['valid']))
                [start_hr, start_mi] = list(map(int, v['time'].split(':')))
                start_dt = datetime(year, mon, mday, start_hr, start_mi).timestamp()
                stop_dt = start_dt + valid * 60
                if int(start_dt) == int(now):
                    task_run = True
                    task = 'start'
                    reset_display()
                    schedule_svg = schedule_icon(v)
                    schedule_svg += message(title, items)
                    return schedule_svg, task_run
                elif int(start_dt) <= int(now) < int(stop_dt):
                    task_run = True
                    schedule_svg = schedule_icon(v)
                    schedule_svg += message(title, items)
                    return schedule_svg, task_run  
                elif int(now) == int(stop_dt):
                    task_run = True
                    task = 'end'
                    reset_display()
                    schedule_svg = schedule_icon(v)
                    schedule_svg += message(title, items)
                    return schedule_svg, task_run
                else:
                    task_run = False
                    schedule_svg = schedule_icon(v)  
    return schedule_svg, task_run

def main(c, c_alarm, c_music, c_schedule, w, h, flag_svg, flag_config, flag_display, flag_png, **kw):   
    while True:
        epoch = int(datetime.now().timestamp())
        if not epoch % c['set_interval'] == 0:
            t.sleep(0.5)
            continue
        else:
            if c['timezone'] == 'local':
                year, mon, mday, hr, mi, sec, wday, yday, isdst = datetime.now().timetuple()
                day = datetime.now().strftime("%-d %B").lower()
                week = datetime.now().strftime("%A").lower()
            else:
                tz = zoneinfo.ZoneInfo(c["timezone"])
                year, mon, mday, hr, mi, sec, wday, yday, isdst = datetime.now(tz).timetuple()
                day = datetime.now(tz).strftime("%-d %B").lower()
                week = datetime.now(tz).strftime("%A").lower()
            # Second
            kw2 = {'w': w, 'h': h, 'radiusX': c['stroke_sec_radius'], 'radiusY': c['stroke_sec_radius'],
                     'innerRadiusX': c['stroke_sec_inner_radius'], 'innerRadiusY': c['stroke_sec_inner_radius'],
                      'v': sec, 'step': 60, 'color': c['color_sec']}
            clock_se = DrawClock(**kw2)
            # Background color
            clock_se_bg_svg = SVGtools.circle(cx=(w * 0.5), cy=(h * 0.5), r=((c['stroke_sec_radius'] + c['stroke_sec_inner_radius']) * 0.5), \
                                    stroke=c['bg_color_sec'], width=(c['stroke_sec_radius'] - c['stroke_sec_inner_radius'])).svg()
            # Minite
            #mi
            kw2 = {'w': w, 'h': h, 'radiusX': c['stroke_min_radius'], 'radiusY': c['stroke_min_radius'],
                    'innerRadiusX': c['stroke_min_inner_radius'], 'innerRadiusY': c['stroke_min_inner_radius'],
                    'v': mi, 'step': 60, 'color': c['color_min']}
            # Background color
            clock_mi_bg_svg = SVGtools.circle(cx=(w * 0.5), cy=(h * 0.5), r=((c['stroke_min_radius'] + c['stroke_min_inner_radius']) * 0.5), \
                                    stroke=c['bg_color_min'], width=(c['stroke_min_radius'] - c['stroke_min_inner_radius'])).svg()
            clock_mi = DrawClock(**kw2)
            # Hour
            a = hr + mi / 60
            #hr = hr + mi / 60
            _hr = a - 12 if a > 12 else a
            kw2 = {'w': w, 'h': h, 'radiusX': c['stroke_hour_radius'], 'radiusY': c['stroke_hour_radius'],
                    'innerRadiusX': c['stroke_hour_inner_radius'], 'innerRadiusY': c['stroke_hour_inner_radius'],
                     'v': _hr, 'step': 12, 'color': c['color_hour']}
            # Background color
            clock_hr_bg_svg = SVGtools.circle(cx=(w * 0.5), cy=(h * 0.5), r=((c['stroke_hour_radius'] + c['stroke_hour_inner_radius']) * 0.5), \
                                    stroke=c['bg_color_hour'], width=(c['stroke_hour_radius'] - c['stroke_hour_inner_radius'])).svg()
            clock_hr = DrawClock(**kw2)
            # Date
            if c['show_date'] == 'True':
                x, y = 775, 520
                font_size = 30
                date_svg = SVGtools.text2(anchor='end', fontweight='bold', fontsize=font_size, x=x, y=y, v=day).svg()
                font_size = 45
                y += 55
                date_svg += SVGtools.text2(anchor='end', fontweight='bold', fontsize=font_size, x=x, y=y, v=week).svg()
            else:
                date_svg = str()
            # Alarm
            alarm_svg, alarm_run = alarm(c=c, c_alarm=c_alarm, hr=hr, mi=mi, sec=sec)
            # Schedule
            schedule_svg, task_run = schedule(c_schedule, hr=hr, mi=mi, sec=sec)
            # Music
            music_svg, music_run = music(c=c, w=w, h=h, c_music=c_music, hr=hr, mi=mi, sec=sec)
            # SVG output; priority: task > alarm > music > clock
            if task_run == True:
                _svg = schedule_svg + date_svg 
            elif alarm_run == True:
                _svg = clock_se_bg_svg + clock_se.svg() + clock_mi_bg_svg + clock_mi.svg() + clock_hr_bg_svg + \
                        clock_hr.svg() + alarm_svg + date_svg
            elif c_music['env']['display'] == 'circle' and music_run == True:
                _svg = clock_mi_bg_svg + clock_mi.svg() + clock_hr_bg_svg + clock_hr.svg() + music_svg + date_svg
            elif c_music['env']['display'] == 'bar' and music_run == True:
                _svg = clock_se_bg_svg + clock_se.svg() + clock_mi_bg_svg + clock_mi.svg() + clock_hr_bg_svg + \
                        clock_hr.svg() + music_svg + date_svg
            else:
                _svg = clock_se_bg_svg + clock_se.svg() + clock_mi_bg_svg + clock_mi.svg() + clock_hr_bg_svg + \
                        clock_hr.svg() + alarm_svg + music_svg + schedule_svg + date_svg
            svg = create_svg(c, _svg)
            if flag_svg == True:
                with open('analog_clock.svg', 'w') as f:
                    f.write(svg)
                    f.close()
                exit(0)
            else:
                flatten_png = 'KindleAnalogClock_flatten.png'
                bytes_png = io.BytesIO()
                svg2png(bytestring=svg, write_to=bytes_png, background_color="white", parent_width=w, parent_height=h)
                png_val = bytes_png.getvalue()
                with Image(blob=png_val) as img:
                    img.rotate(90)
                    img.alpha_channel_types = 'flatten'
                    img.save(filename='/tmp/' + flatten_png)
                    if flag_display == True:
                        display(img)
                img.close()
            if not flag_display == True and not flag_png == True:
                cmd = f'scp /tmp/{flatten_png} root@{kindleIP}:/tmp'
                proc2 = Popen([cmd],shell=True, stdout=PIPE, stderr=PIPE).wait()
                cmd = f'ssh root@{kindleIP} \"cd /tmp; /usr/sbin/eips -g {flatten_png}\"'
                proc3 = Popen([cmd],shell=True, stdout=PIPE, stderr=PIPE)
            t.sleep(0.5)
     
if __name__ == "__main__":
    flag_svg, flag_config, flag_display, flag_png = False, False, False, False
    if 'svg' in sys.argv:
        flag_svg = True
        sys.argv.remove('svg')
    elif 'config' in sys.argv:
        flag_config = True
        sys.argv.remove('config')
    elif 'display' in sys.argv:
        flag_display = True
        sys.argv.remove('display')
    elif 'png' in sys.argv:
        flag_png = True
        sys.argv.remove('png')
    # custom setting    
    if len(sys.argv) > 1:
        setting = sys.argv[1]
    else:
        setting = 'setting.json'          

    setting_alarm = 'alarm.json'
    setting_music ='music.json'
    setting_schedule ='schedule.json'
    with (open(setting, 'r') as f1,
        open(setting_alarm, 'r') as f2,
        open(setting_music, 'r') as f3,
        open(setting_schedule, 'r') as f4):
        c = json.load(f1)['clock']
        c_alarm = json.load(f2)['alarm']
        c_music = json.load(f3)
        c_schedule = json.load(f4)['schedule']
    
    if flag_config == True:
        print(json.dumps(c, ensure_ascii=False, indent=4))
        print(json.dumps(c_alarm, ensure_ascii=False, indent=4))
        print(json.dumps(c_music, ensure_ascii=False, indent=4))
        print(json.dumps(c_schedule, ensure_ascii=False, indent=4))
        exit(0)
        
    w, h = (800, 600) if c['layout'] == 'landscape' else (600, 800)
    kw = {'c': c, 'c_alarm': c_alarm, 'c_music': c_music, 'c_schedule': c_schedule, 'w': w, 'h': h,
                'flag_svg': flag_svg, 'flag_config': flag_config, 'flag_display': flag_display, 'flag_png': flag_png}

    with open('/tmp/kindle-analog-clock.pid', 'w') as f:
        f.write(str(os.getpid()))
    f.close()
        
    main(**kw)


    
