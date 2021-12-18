import inspect
import sys
import threading
import requests
import re
import time
from requests.exceptions import ReadTimeout, ConnectTimeout
from xml.dom import minidom
from .fsapi_exception import *



class FSAPI_Node_Blocked_Exception(Exception):
    def __init__(self, message="Device is controlled from a different controller"):
        self.message = message
        super().__init__(self.message)


class FSAPI_Device_Offline_Exception(Exception):
    def __init__(self, message="Device is offline"):
        self.message = message
        super().__init__(self.message)


class FSAPI_Session_Invalid_Exception(Exception):
    def __init__(self, message="Session is invalid"):
        self.message = message
        super().__init__(self.message)


class FSAPI_Context_Manager:

    def __init__(self, fsapi_reference, pin = "1234"):
        self._access_locker = threading.Lock()
        self._req_session = requests.Session()
        self._fsapi = fsapi_reference
        self._req_session.headers.update({"pin": pin})

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        # time.sleep(0.01)   # to throttle requests
        pass

    def get_new_session(self):
        pass
        
    def invalidate_session(self):
        pass

    def get_request(self, url, params):
        with self._access_locker:
            self._fsapi.write_log(f"get_request: {url} with {params}")
            try:
                result = self._req_session.get(url, params=params, timeout=2)
                if result.status_code == 200:
                    self._fsapi.write_log(f"get_request DONE OK: {url} with {params}")
                    return result.content
                else:
                    self._fsapi.write_log(f"get_request DONE: {url} with {params}, resulted in {result.status_code}")
                    return result.status_code
            except ReadTimeout:
                self._fsapi.write_log(f"get_request ReadTimeout")
                return 408
            except ConnectTimeout:
                self._fsapi.write_log(f"get_request ConnectTimeout")
                return 408

class FSAPI(object):
    _low_level_property_repository_factory = []
    _callback_on_update = None
    _callback_method_on_update = None
    _callback_method_on_update_context = None
    
    """    
    Retry logic:
    In getter und setter un deleter einbauen:
    Wenn 408, dann retry in 2sec, dreimal, danach permanent failed
    Wenn 404, dann session_id erneuern, nochmal probieren, dann permanent failed
    
    """

    @staticmethod
    def register_class(clss, fsapi_property_alias, fsapi_set_method_alias: str, fsapi_type: str):
        typ_key = clss.key.lower()
        
        if fsapi_type == 'void1':
            def executor(s): return s._repository[typ_key].set(1)
            setattr(FSAPI, fsapi_set_method_alias, executor)
        else:
            def getter(s): return s._repository[typ_key].get()
            def setter(s, v): return s._repository[typ_key].set(v)
            def deleter(s): return s._repository[typ_key].dele()
            setattr(FSAPI, fsapi_property_alias, property(getter, setter, deleter))
        
            if fsapi_set_method_alias is not None:
                setattr(FSAPI, fsapi_set_method_alias, setter)
        FSAPI._low_level_property_repository_factory.append(lambda FSAPI_inst: FSAPI_inst._register(clss.__name__))

    @staticmethod
    def register_high_level_property(property_name, getter, setter, dependsOn: [type] = []):
        setattr(FSAPI, property_name, property(getter, setter))

    @staticmethod
    def register_proxy_method(method_name, method_implementation, dependsOn: [type] = []):
        setattr(FSAPI, method_name, method_implementation)

    def __enter__(self):
        pass
    def __exit__(self, type, value, tb):
        self.stop()

    def __init__(self, fsapi_device_url, pin, notification_thread_name=None):
        self._pin = pin
        self._repository = {}
        self.settables = []
        self.gettables = []
        self._access_locker = FSAPI_Context_Manager(self, pin=pin)
        self._notification_thread_name = notification_thread_name
        self._cached_webfsapi = None
        self._fsapi_device_url = fsapi_device_url     
        self._callback_method_log = None
        self._callback_method_on_update = None
        
        for registrator in FSAPI._low_level_property_repository_factory:
            registrator(self)            

    def _register(self, typ_name):
        typ = globals()[typ_name]

        node_instance = typ()
        node_instance._inject_fsapi(self)
        if node_instance.can_get:
            self.gettables.append(node_instance.fsapi_property_alias)
        if node_instance.can_set:
            self.settables.append(node_instance.fsapi_property_alias)
        typ_key = typ.key.lower()

        self._repository[typ_key] = node_instance

    def _get_webfsapi(self):
        if self._cached_webfsapi is None:
            r = requests.get(self._fsapi_device_url)
            xml = minidom.parseString(r.content).firstChild
            webfsapi = next(iter(xml.getElementsByTagName('webfsapi')))
            self._cached_webfsapi = webfsapi.firstChild.data
        return self._cached_webfsapi

    def report(self, prefix="", key_search=".*"):
        for item_key in self._repository:
            if item_key == FSAPI_Node_Notifications.key:
                continue
            if not re.search(key_search, item_key):
                continue
            if self._repository[item_key].can_get:
                yield f"Retrieving: {prefix} {item_key}"
                value = self._repository[item_key].get()
                yield f"    Result: {value}"
                
    def register_callback_function(self, func):
        self._callback_on_update = func
        
    def register_callback_method(self, context, func):
        self._callback_method_on_update_context = context
        self._callback_method_on_update = func

    def register_exception_callback_method(self, context, func):
        self._callback_method_on_error_context = context
        self._callback_method_on_error = func
        
    def register_logging_method(self, context, func):
        self._callback_method_log_context = context
        self._callback_method_log = func

    def stop_listening_to_notifications(self):
        self.write_log("Stopping myself now")
        self._listen_active = False
        try:
            del self.session_id
        except:
            pass
        try:
            self._listen_thread.join(1)
        except:
            pass
    
    def start_listening_to_notifications(self):
        self.write_log("Start Listening to Notifications now")
        if self._notification_thread_name is not None:
            self._listen_thread = threading.Thread(
                target=self._listen, name=self._notification_thread_name + '_FSAPI_notify')
            self._listen_thread.start()

    def __del__(self):
        self.stop_listening_to_notifications()

    def write_log(self, log_txt):
        if self._callback_method_log is not None:
            self._callback_method_log(self._callback_method_log_context, log_txt)
        else:
            print(log_txt)

    def _listen(self):
        # __ = list(self.report())
        time.sleep(5)
        self._listen_active = True
        self.write_log("Listening to changes is enabled now")
        while self._listen_active:
            try:
                self.utilize_notifications()
            except ConnectionError:
                self.write_log("Connection failed, sleeping 10s before trying to get next set of notifications")
                time.sleep(10)
            except (RuntimeError, TypeError, NameError, ValueError, Exception) as e:
                if self._callback_method_on_error is not None:
                    self.write_log("Calling callback on error")
                    try:
                        self._callback_method_on_error(self._callback_method_on_error_context, e)
                    except (RuntimeError, TypeError, NameError, ValueError, Exception) as x:
                        self.write_log("Error-callback failed" + repr(x))
                else:
                    self.write_log("Exception occured in listening to Notifications: " + e)
                    # time.sleep(2)
                    # raise
            except:
                self.write_log("Something really bad happened")
        self.write_log("Listening to changes is disabled now!")

    # Read-only ###################################################################################

    def utilize_notifications(self):
        self.write_log("Utilizing notifications:")
        res = self._notifies
        if isinstance(res, int):
            if res == 404:
                del self.session_id
                return
            else:
                self.write_log(f"Notification with {res}")
                return
        if res is None:
            self.write_log("Notifications with nothing")
            return
        for line in res:
            node = line['node']
            value = line['value']

            if not node in self._repository.keys():
                continue
            self.write_log(f"Updating notified {self._notification_thread_name}: {node} => {self._repository[node].fsapi_property_alias} with {value}")
            self._repository[node]._update_cache(value)
            if self._callback_on_update is not None:
                self._callback_on_update(self, self._repository[node].fsapi_property_alias, value)
            if self._callback_method_on_update is not None:
                self._callback_method_on_update(self._callback_method_on_update_context, self, self._repository[node].fsapi_property_alias, value)


# Order matters: FSAPI needs to be declared before dependend objects can be loaded and registered
# therefor the noqa was added
from .netRemote_session import *  # noqa
from .netRemote_sys import *  # noqa
from .netRemote_sys_caps import *  # noqa
from .netRemote_sys_audio import *  # noqa
from .netRemote_play import *  # noqa
from .netRemote_nav import *  # noqa
from .netRemote_multiroom_caps import *  # noqa
from .netRemote_multiroom_client import *  # noqa
from .netRemote_multiroom_device import *  # noqa
from .netRemote_multiroom_group import *  # noqa

from .fsapi_extensions import *  # noqa
