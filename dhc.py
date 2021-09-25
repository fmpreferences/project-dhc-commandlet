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


def get_highest_resolution_stream(video: YouTube) -> Stream:
    '''returns highest resolution stream
    of a given video

    :param video:
        the video whose streams to check
    :returns:
        the highest resolution stream
    '''
    if (streams := video.streams.filter(file_extension='mp4')) is not None:
        itags = []
        for stream in streams:  # gets highest reso stream obj
            if stream.resolution is not None:
                itags.append((int(stream.itag), int(stream.resolution[:-1])))
        return streams.get_by_itag(max(itags, key=lambda x: x[1])[0])
    else:
        raise ValueError('the object has no valid streams')


def get_highest_bitrate_audio(video: YouTube) -> Stream:
    '''returns highest bitrate audio stream
    of a given video

    :param video:
        the video whose streams to check
    :returns:
        the highest bitrate stream
    '''
    if (streams := video.streams.filter(file_extension='mp3')) is not None:
        itags = []
        for stream in streams:  # gets highest reso stream obj
            if stream.bitrate is not None:
                itags.append((int(stream.itag), int(stream.bitrate)))
        return streams.get_by_itag(max(itags, key=lambda x: x[1])[0])
    else:
        raise ValueError('the object has no valid streams')


def _video_helper(video: YouTube) -> dict:
    '''returns or downloads any requested flags
    from the user. the "meat" of the program

    :param video:
        the video to operate on
    :returns:
        dictionary with all the requested
        properties from the user
    '''
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
        s = get_highest_resolution_stream(video)
        s.download(
            filename=f'{video.title} {VID_URL}.{s.subtype}')
    return video_properties


'''main method'''
if args.playlist or args.channel:
    playlist = None
    PLAYLIST_URL = args.id
    if args.playlist:
        playlist = Playlist(
            f'https://www.youtube.com/playlist?list={PLAYLIST_URL}')
    if args.channel:
        playlist = Channel(
            f'https://www.youtube.com/channel/{PLAYLIST_URL}')
    vprops = [_video_helper(video) for video in playlist.videos]
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
    vprops = _video_helper(video)
    if args.descriptions:
        with open(f'{video.title} {VID_URL}.json', 'w') as json_out:
            json.dump(vprops, json_out, indent=4)
