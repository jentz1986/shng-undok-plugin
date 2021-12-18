from .fsapi_exception import *
from .fsapi_node import *


@FSAPI_Node('str')
class FSAPI_Node_PlayInfoName(object):
    key = 'netRemote.play.info.name'
    max_age = 30
    get_url = "GET/{}"


@FSAPI_Node('str')
class FSAPI_Node_PlayInfoAlbum(object):
    key = 'netRemote.play.info.album'
    max_age = 30
    get_url = "GET/{}"


@FSAPI_Node('str')
class FSAPI_Node_PlayInfoArtist(object):
    key = 'netRemote.play.info.artist'
    max_age = 30
    get_url = "GET/{}"


@FSAPI_Node('u32')
class FSAPI_Node_PlayInfoDuration(object):
    key = 'netRemote.play.info.duration'
    max_age = 30
    get_url = "GET/{}"


@FSAPI_Node('str')
class FSAPI_Node_PlayInfoGraphicUri(object):
    key = 'netRemote.play.info.graphicUri'
    max_age = 30
    get_url = "GET/{}"


@FSAPI_Node('str')
class FSAPI_Node_PlayInfoText(object):
    key = 'netRemote.play.info.text'
    max_age = 30
    get_url = "GET/{}"


@FSAPI_Node('u32')
class FSAPI_Node_PlayPosition(object):
    key = 'netRemote.play.position'
    max_age = 30
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('s8')
class FSAPI_Node_PlayRate(object):
    key = 'netRemote.play.rate'
    max_age = 30
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('bool')  # u8
class FSAPI_Node_PlayRepeat(object):
    key = 'netRemote.play.repeat'
    max_age = 30
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('bool')  # u8
class FSAPI_Node_PlayScrobble(object):
    key = 'netRemote.play.scrobble'
    max_age = 30
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('bool')  # u8
class FSAPI_Node_PlayShuffle(object):
    key = 'netRemote.play.shuffle'
    max_age = 30
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('u8')
class FSAPI_Node_PlayStatus(object):
    key = 'netRemote.play.status'
    max_age = 3
    get_url = "GET/{}"

    PLAY_STATES = {
        0: 'stopped',
        1: 'buffering/loading',
        2: 'playing',
        3: 'paused',
        6: 'multiroom',
    }

    def _convert_from(self, value):
        return self.PLAY_STATES.get(value)

@FSAPI_Node('u8')
class FSAPI_Node_PlayControl(object):
    key = 'netRemote.play.control'
    max_age = 3
    get_url = "GET/{}"
    set_url = "SET/{}"

    PLAY_CONTROL = {
        0: 'stop',
        1: 'play',
        2: 'pause',
        3: 'next',
        4: 'previous',
    }

    def _convert_from(self, value):
        return self.PLAY_CONTROL.get(value)

    def _convert_to(self, value):
        if value is int:
            return value
        conv_val = next(iter([i for i in self.PLAY_CONTROL if self.PLAY_CONTROL[i] == value]))
        if conv_val is None:
            raise RuntimeError("Cannot match your input")
        return conv_val