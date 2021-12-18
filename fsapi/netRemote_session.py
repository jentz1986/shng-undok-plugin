from xml.dom import minidom
from .fsapi_exception import *
from .fsapi_node import *


@FSAPI_Node('raw', '_notifies')
class FSAPI_Node_Notifications:
    key = 'notifications'
    max_age = 0
    get_url = 'GET_NOTIFIES'

    def _parse_value(self, doc: str):
        try:
            if isinstance(doc, int):
                self._fsapi.write_log(f"Notify ended in HTTP-Code: {doc}")
                return doc
            xml = minidom.parseString(doc).firstChild
            if not xml.getElementsByTagName('status')[0].firstChild.data == 'FS_OK':
                self._fsapi.write_log(f"Notify ended in XML: {doc}")
                return None
            ret_store = []
            res = xml.getElementsByTagName('notify')
            for notify in res:
                attrs = {}
                attrs['node'] = str(notify.getAttribute('node')).lower()
                for field in notify.getElementsByTagName('value'):
                    fv = ''
                    for tag_type in ['c8_array', 'u8', 'u32', 's16']:
                        for val in field.getElementsByTagName(tag_type):
                            if val.firstChild is None:
                                fv = None
                            else:
                                fv = val.firstChild.data

                    attrs['value'] = fv
                ret_store.append(attrs)
            
            self._fsapi.write_log(f"Notify ended in updates: {ret_store}")
            return ret_store
        except Exception as e:
            self._fsapi.write_log(f"While parsing [{doc}]: {e}")


@FSAPI_Node('raw', 'session_id')
class FSAPI_Node_Session:
    key = 'sessionId'
    max_age = 3600
    get_url = "CREATE_SESSION"
    del_url = "DELETE_SESSION"

    def _parse_value(self, doc):
        return self._get_xml_single_content(doc, 'sessionId')

    def _call(self, path, extra=None):
        webfsapi_url = self._fsapi._get_webfsapi()
        if not webfsapi_url:
            raise Exception('No server found')

        if path == self.get_url:
            params = dict(pin=self._fsapi._pin)
        else:
            if self._last_value is None:
                return None
            params = dict(
                pin=self._fsapi._pin,
                sid=self._last_value
            )
        url = '%s/%s' % (webfsapi_url, path)
        try:
            with self._fsapi._access_locker as l:
                return l.get_request(url, params=params)
        except Exception as e:
            self._fsapi.write_log("While requesting {} with {}: {}".format(url, params, e))
            raise
