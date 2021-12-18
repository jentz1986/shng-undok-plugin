from .fsapi_node import *


@FSAPI_Node('u8', 'multiroom_group_master_volume')
class FSAPI_Node_Multiroom_Group_MasterVolume(object):
    key = 'netRemote.multiroom.group.masterVolume'
    max_age = 1
    get_url = "GET/{}"
    set_url = "SET/{}"


@FSAPI_Node('str', 'multiroom_group_name')
class FSAPI_Node_Multiroom_Group_Name(object):
    key = 'netRemote.multiroom.group.name'
    max_age = 5
    get_url = "GET/{}"


@FSAPI_Node('str', 'multiroom_group_create', 'create_multiroom_group')
class FSAPI_Node_Multiroom_Group_Create(object):
    key = 'netRemote.multiroom.group.create'
    max_age = 5
    set_url = "SET/{}"


@FSAPI_Node('void1', 'multiroom_group_destroy', 'destroy_multiroom_group')
class FSAPI_Node_Multiroom_Group_Destroy(object):
    key = 'netRemote.multiroom.group.destroy'
    max_age = 5
    set_url = "SET/{}"


@FSAPI_Node('str', 'multiroom_group_add_client', 'add_multiroom_client')
class FSAPI_Node_Multiroom_Group_Add_Client(object):
    key = 'netRemote.multiroom.group.addClient'
    max_age = 5
    set_url = "SET/{}"


@FSAPI_Node('str', 'multiroom_group_id')
class FSAPI_Node_Multiroom_Group_Id(object):
    key = 'netRemote.multiroom.group.id'
    max_age = 5
    get_url = "GET/{}"


@FSAPI_Node('u8', 'multiroom_group_state')
class FSAPI_Node_Multiroom_Group_State(object):
    key = 'netRemote.multiroom.group.state'
    max_age = 5
    get_url = "GET/{}"
    set_url = "SET/{}"
    

@FSAPI_Node('list', 'multiroom_group_attached_clients')
class FSAPI_Node_Multiroom_Group_Attached_Clients(object):
    key = 'netRemote.multiroom.group.attachedClients'
    max_age = 30
    get_url = "LIST_GET_NEXT/{}/-1"



"""



netRemote.multiroom.group.becomeServer
TODO

Method: ??

???


netRemote.multiroom.group.removeClient
TODO

Method: SET

Send the udn of the client as value that you get with netRemote.multiroom.device.listAll


netRemote.multiroom.group.streamable
TODO

Method: GET

???

/fsapi/GET/netRemote.multiroom.group.streamable?pin=1337

<value><u8>1</u8></value>




"""