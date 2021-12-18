from .fsapi_exception import *
from .fsapi_node import *


@FSAPI_Node('list', 'listPresets')
class FSAPI_Node_NavPresets(object):
    key = 'netRemote.nav.presets'
    max_age = 30
    get_url = "LIST_GET_NEXT/{}/-1"


@FSAPI_Node('u32','selectedPreset')
class FSAPI_Node_NavActionSelectPreset(object):
    key = 'netRemote.nav.action.selectPreset'
    max_age = 30
    # get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('u8','navState')
class FSAPI_Node_NavState(object):
    key = 'netRemote.nav.state'
    max_age = 1
    get_url = "GET/{}"
    set_url = "SET/{}"
