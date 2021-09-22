import argparse
from pytube import YouTube, Playlist

ytparser = argparse.ArgumentParser(
    description='Download a whole yt playlist, or some of its attributes')

ytparser.add_argument('id', type=str, help='The list or video id')
ytparser.add_argument('--channel', action='store_true',
                      help='downloads a channel (experimental)')
ytparser.add_argument('--descriptions', action='store_true',
                      help='gets descriptions')
ytparser.add_argument('--playlist', action='store_true',
                      help='downloads a playlist')
ytparser.add_argument('--titles', action='store_true', help='gets titles')
ytparser.add_argument('--videos', action='store_true', help='downloads videos')

args = ytparser.parse_args()
if args.playlist:
    playlist = Playlist(f'https://www.youtube.com/playlist?list={args.id}')
