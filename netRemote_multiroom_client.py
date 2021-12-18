from .fsapi_node import *


@FSAPI_Node('u8', 'multiroom_client_status_1')
class FSAPI_Node_Multiroom_Client_Status_1(object):
    key = 'netRemote.multiroom.client.status1'
    max_age = 2
    get_url = "GET/{}"

@FSAPI_Node('u8', 'multiroom_client_status_2')
class FSAPI_Node_Multiroom_Client_Status_2(object):
    key = 'netRemote.multiroom.client.status2'
    max_age = 2
    get_url = "GET/{}"

@FSAPI_Node('u8', 'multiroom_client_status_3')
class FSAPI_Node_Multiroom_Client_Status_3(object):
    key = 'netRemote.multiroom.client.status3'
    max_age = 2
    get_url = "GET/{}"

@FSAPI_Node('u8', 'multiroom_client_status_4')
class FSAPI_Node_Multiroom_Client_Status_4(object):
    key = 'netRemote.multiroom.client.status4'
    max_age = 2
    get_url = "GET/{}"


@FSAPI_Node('u8', 'multiroom_client_volume_1')
class FSAPI_Node_Multiroom_Client_volume_1(object):
    key = 'netRemote.multiroom.client.volume1'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_volume_2')
class FSAPI_Node_Multiroom_Client_volume_2(object):
    key = 'netRemote.multiroom.client.volume2'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_volume_3')
class FSAPI_Node_Multiroom_Client_volume_3(object):
    key = 'netRemote.multiroom.client.volume3'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_volume_4')
class FSAPI_Node_Multiroom_Client_volume_4(object):
    key = 'netRemote.multiroom.client.volume4'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_volume_5')
class FSAPI_Node_Multiroom_Client_volume_5(object):
    key = 'netRemote.multiroom.client.volume5'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"



@FSAPI_Node('u8', 'multiroom_client_mute_1')
class FSAPI_Node_Multiroom_Client_mute_1(object):
    key = 'netRemote.multiroom.client.mute1'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_mute_2')
class FSAPI_Node_Multiroom_Client_mute_2(object):
    key = 'netRemote.multiroom.client.mute2'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_mute_3')
class FSAPI_Node_Multiroom_Client_mute_3(object):
    key = 'netRemote.multiroom.client.mute3'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"

@FSAPI_Node('u8', 'multiroom_client_mute_4')
class FSAPI_Node_Multiroom_Client_mute_4(object):
    key = 'netRemote.multiroom.client.mute4'
    max_age = 2
    get_url = "GET/{}"
    set_url = "SET/{}"
