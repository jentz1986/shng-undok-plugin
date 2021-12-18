from .fsapi_node import *


@FSAPI_Node('list')
class FSAPI_Node_Multiroom_Device_ListAll(object):
    key = 'netRemote.multiroom.device.listAll'
    max_age = 30
    get_url = "LIST_GET_NEXT/{}/-1"



"""
netRemote.multiroom.device.listAllVersion
TODO

Method: ??

???


netRemote.multiroom.device.serverStatus
TODO

Method: GET

???

/fsapi/GET/netRemote.multiroom.device.serverStatus?pin=1337

<value><u8>1</u8></value>

netRemote.multiroom.device.clientStatus
netRemote.multiroom.device.clientIndex
TODO

Method: GET

???

/fsapi/GET/netRemote.multiroom.device.clientIndex?pin=1337

<value><u8>0</u8></value>

netRemote.multiroom.device.transportOptimisation
TODO

Method: GET

???

/fsapi/GET/netRemote.multiroom.device.transportOptimisation?pin=1337

<status>FS_NODE_DOES_NOT_EXIST</status>

netRemote.multiroom.group.becomeServer
TODO

Method: ??

???


"""