from .fsapi_node import *


@FSAPI_Node('u8', 'multiroom_max_clients')
class FSAPI_Node_Multiroom_Caps_Max_Clients(object):
    key = 'netRemote.multiroom.caps.maxClients'
    max_age = 3600
    get_url = "GET/{}"
    

@FSAPI_Node('u32', 'multiroom_protocol_version')
class FSAPI_Node_Multiroom_Caps_Protocol_Version(object):
    key = 'netRemote.multiroom.caps.protocolVersion'
    max_age = 3600
    get_url = "GET/{}"
