from .fsapi_node import *


@FSAPI_Node('str', fsapi_property_alias = 'friendly_name')
class FSAPI_Node_FriendlyName(object):
    key = 'netRemote.sys.info.friendlyName'
    max_age = 3600
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('str', fsapi_property_alias = 'radio_id')
class FSAPI_Node_RadioId(object):
    key = 'netRemote.sys.info.radioId'
    max_age = 3600
    get_url = "GET/{}"



@FSAPI_Node('str', fsapi_property_alias = 'version')
class FSAPI_Node_Version(object):
    key = 'netRemote.sys.info.version'
    max_age = 3600
    get_url = "GET/{}"


@FSAPI_Node('u32', fsapi_property_alias = 'mode_key')
class FSAPI_Node_Mode(object):
    key = 'netRemote.sys.mode'
    max_age = 10
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u32', fsapi_property_alias = 'sleep_timer')
class FSAPI_Node_Sleep(object):
    key = 'netRemote.sys.sleep'
    max_age = 1
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('bool', fsapi_property_alias = 'power')
class FSAPI_Node_Power(object):
    key = 'netRemote.sys.power'
    max_age = 5
    get_url = "GET/{}"
    set_url = "SET/{}"
