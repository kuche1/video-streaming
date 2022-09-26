#! /usr/bin/env python3

import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import pytube # python3 -m pip install pytube
import random
import socket
import ssl
import time
import threading
import urllib

HERE = os.path.dirname(os.path.realpath(__file__))

HOSTNAME = ''
PORT = 8085
HASHING_ALG = hashlib.sha512

MAX_VOTES_PER_VIDEO = 3

class g:
    default_playlist = [
        'https://www.youtube.com/watch?v=I8_a-iWOT2U',
    ]

    user_votes = []
    user_ips = []

    video_starts_at = 0
    video_ends_at = 0
    video_dir = ''
    video_type = ''

    changing_video_lock = threading.Lock()

class MyServer(BaseHTTPRequestHandler):

    def hash(s, text):
        m = HASHING_ALG()
        m.update(text.encode('utf-8'))
        return m.hexdigest()

    def send_str(s, txt):
        assert type(txt) == str
        s.wfile.write(txt.encode('utf-8'))

    def try_video(s, url):
        try:
            pytube.YouTube(url)
        except pytube.exceptions.RegexMatchError:
            return 'Invalid link'
        except pytube.exceptions.VideoUnavailable:
            return 'Video unavailable'
        except pytube.exceptions.LiveStreamError:
            return 'Livestreams are not allowed'

    def change_video(s, url):
        hashed_url = s.hash(url)

        vid_mime = 'video/mp4'
        vid_dir = f'/cache/{hashed_url}'+'.mp4' # TODO do not use `cache` folder, use tmp files instead
        vid_duration_dir = f'{HERE}/{vid_dir}_length' # TODO might be dangerous
        
        g.video_dir = vid_dir#
        g.video_type = vid_mime#
        
        download_video = True
        if os.path.isfile(vid_dir) and os.path.isfile(vid_duration_dir):
            print('video in cache')
            f = open(vid_duration_dir)
            vid_duration = f.read()
            f.close()
            try:
                float_vid_duration = float(vid_duration)
            except ValueError:
                print(f'video length file corrupted: {vid_duration_dir}')
            else:
                download_video = False

        if download_video:
            try:
                yt = pytube.YouTube(url)
            except KeyError:#?????? ?????? ?????? ????? ????? ????? ???? ???? ??? ??? ?? ?? kur za youtube kur za youtube kur za youtube kur za youtube kur za youtube kur za youtube kur za youtube kur za youtube kur za youtube kur za youtube
                print('pak smotaniq KeyError')
                return s.change_video(url)
            vid_duration = yt.length
            float_vid_duration = float(vid_duration)
            print(f'downloading: {url}')
            yt.streams.filter(mime_type='video/mp4').first().download(HERE+'/cache/', hashed_url+'.mp4')
            print(f'downloaded: {url}')
            f = open(vid_duration_dir,'w')
            f.write(str(vid_duration))
            f.close()

        g.video_starts_at = time.time()
        g.video_ends_at = g.video_starts_at + float_vid_duration

    # methods

    def do_GET(s):

        if s.path == '/':
            s.send_response(200)
            s.send_header('Content-type', 'text/html')
            s.send_header('Accept-Ranges', 'bytes=0-100')
            s.end_headers()

            with open(f'{HERE}/responses/video-streaming.html', 'rb') as f:
                s.wfile.write(f.read())
        
        elif s.path.startswith('/cache/'):
            with open(f'{HERE}/{s.path}', 'rb') as f:
                s.send_response(200)
                #s.send_header('Content-type', 'video/mp4') # TODO read this from a file
                s.send_header('Accept-Ranges', 'bytes=0-100')
                s.end_headers()

                s.wfile.write(f.read())

        else:

            s.send_response(200)
            s.send_header('Content-type', 'text/html')
            s.send_header('Accept-Ranges', 'bytes=0-100')
            s.end_headers()
            s.wfile.write(bytes('<html><head><title>https://pythonbasics.org</title></head>', 'utf-8'))
            s.wfile.write(bytes('<p>Request: %s</p>' % s.path, 'utf-8'))
            s.wfile.write(bytes('<body>', 'utf-8'))
            s.wfile.write(bytes('<p>sadscagfrsvgrevgtdvfhgfd.</p>', 'utf-8'))
            s.wfile.write(bytes('</body></html>', 'utf-8'))

    def do_GET_VIDEO_DIR_AND_TIME_AND_TYPE(s):

        video_time_left = g.video_ends_at - time.time()
        if video_time_left <= 0:
            g.changing_video_lock.acquire()
            try:
                print('changing video')
                g.user_ips = []
                if g.user_votes:
                    
                    competitors = {}
                    for url in g.user_votes:
                        if url in competitors:
                            competitors[url] += 1
                        else:
                            competitors[url] = 1
                            
                    most_votes = 0
                    winner = ''
                    for url in competitors:
                        votes = competitors[url]
                        if votes > most_votes:
                            winner = url
                            most_votes = votes
                    while winner in g.user_votes:
                        g.user_votes.remove(winner)
                else:
                    winner = random.choice(g.default_playlist)

                s.change_video(winner)
            finally:
                g.changing_video_lock.release()

        video_time_passed = time.time() - g.video_starts_at
        resp=f'{g.video_dir};{video_time_passed};{g.video_type}'
        print(f'{resp=}')

        s.send_response(200)
        s.send_header('Accept-Ranges', 'bytes=0-100')
        s.end_headers()

        s.send_str(resp)
    
    def do_VOTE(s):
        s.send_response(200)
        s.send_header('Accept-Ranges', 'bytes=0-100')
        s.end_headers()

        assert s.path[0] == '/'
        vote = urllib.parse.unquote_plus(s.path[1:])
        print(f'{vote=}')

        ip = s.address_string()

        votes_left = MAX_VOTES_PER_VIDEO - g.user_ips.count(ip)
        if votes_left <= 0:
            s.send_str('You have exceeded the maximum number of votes for this video.')
            return

        res = s.try_video(vote)
        if res:
            s.send_str(f'error while processing video: {res}')
        else:
            g.user_ips.append(ip)
            g.user_votes.append(vote)
            s.send_str(f'Your vote has been received. You have {votes_left-1} vote(s) left.')

    def do_GET_VOTES(s):
        s.send_response(200)
        s.send_header('Accept-Ranges', 'bytes=0-100') # TODO fuck this and all other instances (fuck google chrome)
        s.end_headers()

        # TODO this is giga shit
        count = {}

        for vote in g.user_votes:
            if vote in count:
                count[vote] += 1
            else:
                count[vote] = 1

        for key in count:
            value = count[key]
            s.send_str(f'[{value}] {key}\n')


if __name__ == '__main__':        
    webServer = HTTPServer((HOSTNAME, PORT), MyServer)

    webServer.socket = ssl.wrap_socket(
        webServer.socket, 
        keyfile=os.path.join(HERE, 'certs', 'private.key'),
        certfile=os.path.join(HERE, 'certs', 'selfsigned.crt'),
        server_side=True,
    )

    webServer.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print(f'running on `https://{HOSTNAME}:{PORT}`')

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('stopped')
