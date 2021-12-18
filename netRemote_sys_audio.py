from .fsapi_exception import *
from .fsapi_node import *


@FSAPI_Node('bool', 'mute')
class FSAPI_Node_Mute(object):
    key = 'netRemote.sys.audio.mute'
    max_age = 5
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('u8', 'volume')
class FSAPI_Node_Volume(object):
    key = 'netRemote.sys.audio.volume'
    max_age = 5
    get_url = "GET/{}"
    set_url = "SET/{}"
