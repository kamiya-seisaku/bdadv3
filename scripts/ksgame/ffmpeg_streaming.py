from ffmpeg_streaming import Formats, Bitrate, Representation, Size
from ffmpeg_streaming import (HLS, DASH)

_720p = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))
_480p = Representation(Size(854, 480), Bitrate(1024 * 1024, 192 * 1024))
_360p = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))

hls = HLS(Formats.h264())
hls.representations(_720p, _480p, _360p)
hls.output('C:\\tmp\\hls.m3u8')
