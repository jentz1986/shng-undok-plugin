from .fsapi_node import *


@FSAPI_Node('list', 'valid_modes')
class FSAPI_Node_Valid_Modes(object):
    key = 'netRemote.sys.caps.validModes'
    max_age = 3600
    get_url = "LIST_GET_NEXT/{}/-1"

@FSAPI_Node('u8', 'volume_steps')
class FSAPI_Node_Volume_Steps(object):
    key = 'netRemote.sys.caps.volumeSteps'
    max_age = 3600
    get_url = "GET/{}"
