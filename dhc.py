import argparse
from pytube import YouTube, Playlist
from pytube.contrib.channel import Channel
from pytube.streams import Stream
import json
import requests

ytparser = argparse.ArgumentParser(
    description='Download a whole yt playlist, or some of its attributes')

ytparser.add_argument('id', type=str, help='The list or video id')
ytparser.add_argument('-c', '--channel', action='store_true',
                      help='downloads a channel (experimental)')
ytparser.add_argument('-d', '--descriptions', action='store_true',
                      help='gets descriptions')
ytparser.add_argument('-p', '--playlist', action='store_true',
                      help='downloads a playlist')
ytparser.add_argument(
    '-t', '--thumbnails', action='store_true', help='gets thumbnails')
ytparser.add_argument(
    '-v', '--videos', action='store_true', help='downloads videos')

args = ytparser.parse_args()

'''really bad method originally used to read stream from string
representation

i have no clue if it's borrowed (stolen) or not, i actually
dont think it is bc i could have written something so ugly
'''


def readable_stream(stream: Stream) -> dict:
    properties = str(stream)[9:-1].split(' ')
    properties = [p.split('=') for p in properties]
    d = {}
    for p in properties:
        d[p[0]] = p[1][1:-1]
    return d


'''returns highest reso stream

maybe a cleaner solution is here but this is the most
readable to me
'''


def get_highest_resolution_stream(video: YouTube) -> Stream:
    if (streams := video.streams.filter(file_extension='mp4')) is not None:
        itags = []
        resolutions = []
        for s in streams:  # gets highest reso stream obj
            streaminfo = readable_stream(s)
            if 'res' in streaminfo:
                itags.append(int(streaminfo['itag']))
                resolutions.append(int(streaminfo['res'][:-1]))
        return streams.get_by_itag(
            itags[resolutions.index(max(resolutions))])
    else:
        raise ValueError('the object has no valid streams')


'''does all the necessary operations for this cmdlet to
work

made to remove duplicate code
'''


def video_helper(video: YouTube) -> dict:
    global args
    VID_URL = video.video_id
    video_properties = {}
    if args.descriptions:
        video_properties[VID_URL] = {
            'title': video.title, 'description': video.description}
    if args.thumbnails:
        url = video.thumbnail_url
        with open(f'{video.title} {VID_URL}.{url.split(".")[-1]}', 'wb') as thumbnail:
            r = requests.get(url)
            thumbnail.write(r.content)
    if args.videos:
        get_highest_resolution_stream(video).download()
    return video_properties


'''script also from og version

refactored'''

if args.playlist or args.channel:
    playlist = None
    PLAYLIST_URL = args.id
    if args.playlist:
        playlist = Playlist(
            f'https://www.youtube.com/playlist?list={PLAYLIST_URL}')
    if args.channel:
        playlist = Channel(
            f'https://www.youtube.com/channel/{PLAYLIST_URL}')
    vprops = [video_helper(video) for video in playlist.videos]
    if args.descriptions:
        if args.playlist:
            fname = f'{playlist.title} {PLAYLIST_URL}.json'
        if args.channel:
            fname = f'{playlist.channel_name} {PLAYLIST_URL}.json'
        with open(fname, 'w') as json_out:
            json.dump(vprops, json_out, indent=4)
else:
    VID_URL = args.id
    video = YouTube(f'https://www.youtube.com/watch?v={VID_URL}')
    vprops = video_helper(video)
    if args.descriptions:
        with open(f'{video.title} {VID_URL}.json', 'w') as json_out:
            json.dump(vprops, json_out, indent=4)
