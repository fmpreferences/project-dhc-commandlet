import argparse
from pytube import YouTube, Playlist
from pytube.streams import Stream

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
    '-t', '--titles', action='store_true', help='gets titles')
ytparser.add_argument(
    '-v', '--videos', action='store_true', help='downloads videos')

args = ytparser.parse_args()

'''really bad method originally used to read stream from string
representation

i have no clue if it's borrowed (stolen) or not, i actually
dont think it is bc i could have written something so trash
'''


def readable_stream(stream: Stream) -> dict:
    properties = str(stream)[9:-1].split(' ')
    properties = [p.split('=') for p in properties]
    d = {}
    for p in properties:
        d[p[0]] = p[1][1:-1]
    return d


'''script also from og version

ok.'''
if args.playlist:
    playlist = Playlist(f'https://www.youtube.com/playlist?list={args.id}')
    for video in playlist.videos:
        if (streams := video.streams.filter(file_extension='mp4')) is not None:
            itags = []
            resolutions = []
            for s in streams:  # gets highest reso stream obj
                streaminfo = readable_stream(s)
                if 'res' in streaminfo:
                    itags.append(int(streaminfo['itag']))
                    resolutions.append(int(streaminfo['res'][:-1]))
            streams.get_by_itag(
                itags[resolutions.index(max(resolutions))]).download()
        else:
            print('download failed')