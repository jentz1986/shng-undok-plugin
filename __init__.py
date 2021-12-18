#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2019 Jens Höppner                      mail@jens-hoeppner.de
#########################################################################
#  This file is part of SmartHomeNG.
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.4 and
#  upwards.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from requests import Session
from typing import Pattern, Dict, Union
import re
import time

from lib.model.smartplugin import *
from lib.item import Items
from datetime import datetime, timedelta
from .webif import WebInterface

from plugins.undok.fsapi.fsapi_core import FSAPI, FSAPI_Node_Blocked_Exception
import ruamel.yaml as yaml
from requests.exceptions import ConnectionError
import json
import traceback


class UndokConst(object):
    PARAMETER_URL = 'undok_device_url'
    PARAMETER_PIN = 'undok_pin'
    PARAMETER_CYCLE_TIME = 'poll_cycle_time'
    PARAMETER_LISTEN_NOTIFIES = 'listen_to_notifications'

    ATTR_TYPE = 'undok_type'


class UndokItemIssue(object):
    def __init__(self, itemPath: str):
        self.issues = []
        self.item = itemPath
        self.worst_level = 0

    def append_issue(self, issue, level):
        if self.issues.__contains__(issue):
            return
        self.issues.append(issue)
        if self.worst_level < level:
            self.worst_level = level

    def get_issues(self):
        return self.issues

    def get_worst_level(self):
        return self.worst_level


class UndokClientModel():

    def __init__(self, api: FSAPI):
        self._items = []
        self._items_with_issues = {}
        self._api = api

    def append_item(self, item):
        self._items.append(item)

    def append_item_issue(self, item, issue, level):
        ipath = item.path()
        if not self._items_with_issues.__contains__(ipath):
            self._items_with_issues[ipath] = UndokItemIssue(ipath)

        self._items_with_issues[ipath].append_issue(issue, level)

    def get_items_with_issues_count(self):
        return len(self._items_with_issues)

    def get_items_with_issues(self):
        for x in self._items_with_issues:
            yield self._items_with_issues[x]

    def get_item_issues(self, item_path):
        if not self._items_with_issues.__contains__(item_path):
            return UndokItemIssue(item_path)
        return self._items_with_issues[item_path]

    def get_item_count(self):
        """
        Returns number of added items
        """
        return len(self._items)

    def get_items(self, filter=None):
        """
        Returns added items

        :return: array of items held by the device
        """
        to_ret = []
        if filter is None:
            return self._items

        for i in self._items:
            if filter(i):
                to_ret.append(i)
        return to_ret

    def get_url(self):
        return self._api.fsapi_device_url

    def get_pin(self):
        return self._api._pin


class UndokClient(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """

    PLUGIN_VERSION = '1.6.1'
    
    def __init__(self, sh, *args, **kwargs):
        """
        Initalizes the plugin. The parameters describe for this method are pulled from the entry in plugin.yaml.
        """

        from bin.smarthome import VERSION
        if '.'.join(VERSION.split('.', 2)[:2]) <= '1.5':
            self.logger = logging.getLogger(__name__)
            
        self.logger.debug("Initialization")

        # get the parameters for the plugin (as defined in metadata plugin.yaml):
        self._undok_url = self.get_parameter_value(UndokConst.PARAMETER_URL)
        self._undok_pin = self.get_parameter_value(UndokConst.PARAMETER_PIN)
        
        api = FSAPI(self._undok_url, self._undok_pin, 'undok_' + self.get_instance_name())
        api.register_callback_method(self, self.api_property_updated)
        api.register_exception_callback_method(self, self.api_exception)
        api.register_logging_method(self, self.log_it)

        self._model = UndokClientModel(api)

        # cycle time in seconds, only needed, if hardware/interface needs to be
        # polled for value changes by adding a scheduler entry in the run method of this plugin
        # (maybe you want to make it a plugin parameter?)
        self._cycle = self.get_parameter_value(UndokConst.PARAMETER_CYCLE_TIME)
        self._logging = True
        
        # self.metadata.itemdefinitions['undok_type']['valid_list']
        
        self._valid_types = set(self.metadata.itemdefinitions['undok_type']['valid_list'])
        self._poll_types = set(api.gettables) & self._valid_types
        self._update_types = set(api.settables) & self._valid_types

        self.init_webinterface()

        return

    def run(self):
        """
        Run method for the plugin
        """
        # setup scheduler for device poll loop   (disable the following line, if you don't need to poll the device. Rember to comment the self_cycle statement in __init__ as well
        if self._cycle > 0:
            self.scheduler_add('poll_undok_' + self.get_instance_name(), self.poll_device, cycle=self._cycle)

        self.alive = True
        
        # TODO: Transfer to web-interface
        # self.logger.debug("Configured for Poll: " + str(self._poll_types))
        # self.logger.debug("Configured for Update: " + str(self._update_types))

        try:
            self.poll_device()
            
            if self.get_parameter_value(UndokConst.PARAMETER_LISTEN_NOTIFIES):
                self._model._api.start_listening_to_notifications()
        except Exception as e:
            self.api_exception(self, e)

        # self._logging = False #TODO: Why?
        
    def api_exception(self, origin, e: Exception):        
        if isinstance(e, ConnectionError):
            self.logger.warn("Connection to device failed, sleeping for 1s now")
            # time.sleep(1)
            # self.stop()
            # TODO Re-enable after ...
        else:
            self.logger.error(repr(e))


    def log_it(self, origin, log_txt):
        self.logger.debug(log_txt)
        
    def stop(self):
        """
        Stop method for the plugin
        """
        try:
            self._model._api.stop_listening_to_notifications()
            self.logger.debug("Logout done")
        except:
            self.logger.warning("Exception during logout")
        self.alive = False

    def _log_item_info(self, item, msg: str, enable_logging=True, defaulting=False):
        if defaulting:
            self._model.append_item_issue(item, "2: " + msg, 2)
        else:
            self._model.append_item_issue(item, "1: "+msg, 1)

        if enable_logging:
            self.logger.info(msg + " in item " + item.path())

    def _log_item_warning(self, item, msg: str, enable_logging=True):
        self._model.append_item_issue(item, "3: "+msg, 3)
        if enable_logging:
            self.logger.warning(msg + " in item " + item.path())

    def _log_item_error(self, item, msg: str, enable_logging=True):
        self._model.append_item_issue(item, "4: " + msg, 4)
        if enable_logging:
            self.logger.error(msg + " in item " + item.path())

    def _get_attribute_recursive(self, item, item_type: str, check=None, enable_logging=True, leaf_item=None):
        if item is None:
            self._log_item_warning(leaf_item, "No {} attribute provided".format(item_type), enable_logging)
            return None
        if leaf_item is None:
            leaf_item = item

        try:
            if item_type in item.conf:
                if not check is None:
                    if not check(item, item_type, leaf_item):
                        return None
                if not (item.path() == leaf_item.path()):
                    self._log_item_info(leaf_item, "{} attribute provided from {}".format(
                        item_type, item.path()), enable_logging)
                return self.get_iattr_value(item.conf, item_type)
        except AttributeError:
            self._log_item_warning(leaf_item, "No {} attribute provided".format(item_type), enable_logging)
            return None
        return self._get_attribute_recursive(item.return_parent(), item_type, check, enable_logging, leaf_item)

    def _get_one_of_attr_recursive(self, item, item_types: list, check=None, enable_logging=True, leaf_item=None):
        if item is None:
            self._log_item_warning(leaf_item, "No {} attribute provided".format(json.dump(item_types)), enable_logging)
            return None
        if leaf_item is None:
            leaf_item = item

        for item_type in item_types:
            try:
                if item_type in item.conf:
                    if not check is None:
                        if not check(item, item_type, leaf_item):
                            return None
                    if not (item.path() == leaf_item.path()):
                        self._log_item_info(leaf_item, "{} attribute provided from {} ".format(
                            item_type, item.path()), enable_logging)

                    return self.get_iattr_value(item.conf, item_type)
            except AttributeError:
                self._log_item_warning(leaf_item, "No {} attribute provided".format(item_type), enable_logging)
                return None
        return self._get_one_of_attr_recursive(item.return_parent(), item_types, check, enable_logging, leaf_item)

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference
        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.
        """
        if not self.has_iattr(item.conf, UndokConst.ATTR_TYPE):
            return

        i_attr = self.get_iattr_value(item.conf, UndokConst.ATTR_TYPE)
        if i_attr in self._valid_types:
            self._model.append_item(item)
            return self.update_item
        else:
            self._log_item_error(item, "{} {} unknown".format(UndokConst.ATTR_TYPE, i_attr))
            self._model.append_item(item)

    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        # if 'xxx' in logic.conf:
        # self.function(logic['name'])
        pass

    def _update_fsapi_with_item(self, item, item_type, func):
        if self._item_filter(item, UndokConst.ATTR_TYPE, item_type):
            try:
                func(item)
            except Exception as e:
                self._log_item_error(item, "HERE! " + repr(e), self._logging)

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Item has been updated

        This method is called, if the value of an item has been updated by SmartHomeNG.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        if caller != self.get_shortname():
            self.logger.debug("update_item was called with item '{}' from caller '{}', source '{}' and dest '{}'".format(item, caller, source, dest))
            for u_type in self._update_types:
                self._update_fsapi_with_item(item, u_type, lambda i: setattr(self._model._api, u_type, i()))


    def _item_filter(self, item, attr_type, attr_val):
        if not self.has_iattr(item.conf, attr_type):
            return False
        if attr_val == self.get_iattr_value(item.conf, attr_type):
            return True
        return False

    def _poll_with_undok_type(self, undok_type):
        # find all items that have the undok_type attribute set to the given value:
        # apply func to item and set the value accordingly
        for item in self._model.get_items(lambda i: self._item_filter(i, UndokConst.ATTR_TYPE, undok_type)):
            try:
                current_value = item()
                new_value = getattr(self._model._api, undok_type)
                self.logger.debug(f"Setting (device -> shng) {undok_type} from {current_value} to {new_value}")
                item(new_value, self.get_shortname())
            except ConnectionError:
                # kills further processing in this round.
                raise
            except Exception as e:
                # log the error for this specific poll type and proceed with next item
                self._log_item_error(item, repr(e), self._logging)

    def api_property_updated(self, origin, property_name: str, new_value):
        self.logger.debug(f"property {property_name} in instance {self.get_instance_name()} was updated from outside")
        for item in self._model.get_items(lambda i: self._item_filter(i, UndokConst.ATTR_TYPE, undok_type)):
            item(new_value, self.get_shortname())

    def poll_device(self):
        """
        Polls for updates
        """
        if not self.alive:
            self.logger.debug("poll_device: Skipped as not alive")
            return
        self.logger.debug("poll_device: Start")
        try:
            for undok_type in self._poll_types:
                self._poll_with_undok_type(undok_type)
            self.logger.debug("poll_device: Finished")
        except ConnectionError as ex:
            self.logger.warn("poll_device: Failed to reach device: " + repr(ex))

    def init_webinterface(self):
        """"
        Initialize the web interface for this plugin

        This method is only needed if the plugin is implementing a web interface
        """
        try:
            # try/except to handle running in a core version that does not support modules
            self.mod_http = Modules.get_instance().get_module('http')
        except:
            self.mod_http = None
        if self.mod_http == None:
            self.logger.error("Not initializing the web interface")
            return False

        import sys
        if not "SmartPluginWebIf" in list(sys.modules['lib.model.smartplugin'].__dict__):
            self.logger.warning("Web interface needs SmartHomeNG v1.5 and up. Not initializing the web interface")
            return False

        # set application configuration for cherrypy
        webif_dir = self.path_join(self.get_plugin_dir(), 'webif')
        config = {
            '/': {
                'tools.staticdir.root': webif_dir,
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static'
            }
        }

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(webif_dir, self),
                                     self.get_shortname(),
                                     config,
                                     self.get_classname(), self.get_instance_name(),
                                     description='')

        return True

    def perform_or_unblock_and_retry(self, action, num_retries = 3):
        success = False
        for i in range(num_retries):
            try:
                action()
                success = True
            except FSAPI_Node_Blocked_Exception:
                self.logger.debug(f"Need to unblock and retry {i}")            
                self._model._api.navState = 1
            if success:
                self.logger.debug(f"Successful at try {i}")
                break
        if not success:
            self.logger.warning(f"Unable to perform action after {num_retries} retries")

    def set_power(self, to_state):
        self.logger.debug(f"Set power to {to_state}")
        self._model._api.power = to_state

    def set_mode(self, to_mode):
        self.logger.debug(f"Set mode to {to_mode}")
        self._model._api.mode = to_mode

    def set_volume(self, to_volume):
        self.logger.debug(f"Set volume to {to_volume}")
        self._model._api.volume = to_volume

    def select_preset(self, preset):
        def do_select_preset():
            self._model._api.selectedPreset = preset
            
        self.logger.debug(f"Selecting preset {preset}")
        self.perform_or_unblock_and_retry(do_select_preset)
        self.logger.debug(f"Selected preset {preset}")

    def get_multiroom_peers_from_friendly_names(self, friendly_names):
        all_peers = self._model._api.multiroom_peers
        requested_peers = []

        for peer in all_peers:
            if peer["friendlyname"] in friendly_names:
                requested_peers.append(peer)

        return requested_peers

    def create_multiroom_group(self, name, peers):
        def do_create_multiroom_group():
            self._model._api.create_multiroom_group(name)
            for peer in peers:
                self._model._api.add_multiroom_client(peer["udn"])
            
        self.logger.debug(f"create_multiroom_group {name}")
        self.perform_or_unblock_and_retry(do_create_multiroom_group)
        self.logger.debug(f"created_multiroom_group {name}")

    def destroy_multiroom_group(self):
        def do_destroy_multiroom_group():
            self._model._api.destroy_multiroom_group()
            
        self.logger.debug(f"destroy_multiroom_group")
        self.perform_or_unblock_and_retry(do_destroy_multiroom_group)
        self.logger.debug(f"destroyed_multiroom_group")
