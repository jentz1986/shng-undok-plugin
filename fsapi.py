# Copyright 2014 Dan Krause
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from lxml import objectify
from lxml.etree import XMLSyntaxError


class FSAPI(object):
    RW_MODES = {
        0: 'internet',
        1: 'spotify',
        2: 'local_music',
        3: 'music',
        4: 'dab',
        5: 'fm',
        6: 'bluetooth',
        7: 'aux',
    }

    PLAY_STATES = {
        0: 'stopped',
        1: 'unknown',
        2: 'playing',
        3: 'paused',
    }

    EQS = {
        0: 'custom',
        1: 'normal',
        2: 'flat',
        3: 'jazz',
        4: 'rock',
        5: 'movie',
        6: 'classic',
        7: 'pop',
        8: 'news',
    }

    def __init__(self, fsapi_device_url, pin):
        self._pin = pin
        self._sid = None  # session ID
        self._webfsapi = None
        self.fsapi_device_url = fsapi_device_url

        self._webfsapi = self._get_fsapi_endpoint()
        self._sid = self.create_session()

    def _get_fsapi_endpoint(self):
        r = requests.get(self.fsapi_device_url)
        doc = objectify.fromstring(r.content)
        return doc.webfsapi.text

    def create_session(self):
        doc = self._call('CREATE_SESSION')
        return doc.sessionId.text

    def _call(self, path, extra=None, return_string=False):
        if not self._webfsapi:
            raise Exception('No server found')

        if type(extra) is not dict:
            extra = dict()

        params = dict(
            pin=self._pin,
            sid=self._sid,
        )

        params.update(**extra)

        r = requests.get('%s/%s' % (self._webfsapi, path), params=params)
        if return_string:
            return r.content
        else:
            return objectify.fromstring(r.content)

    def __del__(self):
        try:
            self._call('DELETE_SESSION')
        except TypeError:
            pass

    # Read-only ###################################################################################

    @property
    def version(self):
        doc = self._call('GET/netRemote.sys.info.version')
        return doc.value.c8_array.text

    @property
    def play_status(self):
        doc = self._call('GET/netRemote.play.status')
        return self.PLAY_STATES.get(doc.value.u8)

    @property
    def play_info_name(self):
        doc = self._call('GET/netRemote.play.info.name')
        return doc.value.c8_array.text or ''

    @property
    def play_info_text(self):
        doc = self._call('GET/netRemote.play.info.text')
        return doc.value.c8_array.text or ''

    @property
    def eq_bands(self):
        doc = self._call('LIST_GET_NEXT/netRemote.sys.caps.eqBands/-1', dict(
            maxItems=100,
        ))
        if not doc.status == 'FS_OK':
            return None

        ret = list()
        for index, item in enumerate(list(doc.iterchildren('item'))):
            temp = dict(band=index)
            for field in list(item.iterchildren()):
                temp[field.get('name')] = list(field.iterchildren()).pop()
            ret.append(temp)

        return ret

    @property
    def notifications(self):
        try:
            doc = self._call('GET_NOTIFIES')
            if doc.status != 'FS_OK':
                return None
            return {
                'node': doc.notify.get('node'),
                'value': list(doc.notify.value.iterchildren()).pop(),
            }
        except XMLSyntaxError:
            return None

    @property
    def valid_modes(self):
        doc = self._call('LIST_GET_NEXT/netRemote.sys.caps.validModes/-1', dict(maxItems=100))

        if not doc.status == 'FS_OK':
            return None

        ret = list()
        for index, item in enumerate(list(doc.iterchildren('item'))):
            temp = dict(index=index)
            skip = False
            for field in list(item.iterchildren()):
                fn = field.get('name')
                ct = list(field.iterchildren()).pop()
                if fn == 'selectable':
                    if ct == 0:
                        skip = True
                elif fn == 'modetype':
                    continue
                else:
                    temp[fn] = ct

            if not skip:
                ret.append(temp)

        return ret

    # Read-write ##################################################################################

    def _get_volume(self):
        doc = self._call('GET/netRemote.sys.audio.volume')
        return doc.value.u8.text

    def _set_volume(self, value):
        doc = self._call('SET/netRemote.sys.audio.volume', dict(value=value))
        return doc.status == 'FS_OK'

    volume = property(_get_volume, _set_volume)

    def _get_friendly_name(self):
        doc = self._call('GET/netRemote.sys.info.friendlyName')
        return doc.value.c8_array.text

    def _set_friendly_name(self, value):
        doc = self._call('SET/netRemote.sys.info.friendlyName', dict(value=value))
        return doc.status == 'FS_OK'

    friendly_name = property(_get_friendly_name, _set_friendly_name)

    def _get_mute(self):
        doc = self._call('GET/netRemote.sys.audio.mute')
        return bool(doc.value.u8)

    def _set_mute(self, value=False):
        if type(value) is not bool:
            raise RuntimeError('Mute must be boolean')
        doc = self._call('SET/netRemote.sys.audio.mute', dict(value=int(value)))
        return doc.status == 'FS_OK'

    mute = property(_get_mute, _set_mute)

    def _get_power(self):
        doc = self._call('GET/netRemote.sys.power')
        return bool(doc.value.u8)

    def _set_power(self, value=False):
        if type(value) is not bool:
            raise RuntimeError('Mute must be boolean, not `%s`' % type(value))

        doc = self._call('SET/netRemote.sys.power', dict(value=int(value)))
        return doc.status == 'FS_OK'

    power = property(_get_power, _set_power)

    def _get_mode(self):
        doc = self._call('GET/netRemote.sys.mode')

        print(doc.value.u32)

        modes = self.RW_MODES
        # modes.update(self.RO_MODES)
        return modes.get(doc.value.u32)

    def _set_mode(self, value):
        modes = {v: k for k, v in self.RW_MODES.items()}
        if value not in modes:
            raise RuntimeError('Not allowed to set mode to `%s`' % value)

        doc = self._call('SET/netRemote.sys.mode', dict(value=modes.get(value)))
        return doc.status == 'FS_OK'

    mode = property(_get_mode, _set_mode)

    def _get_eq_preset(self):
        doc = self._call('GET/netRemote.sys.audio.eqPreset')
        return self.EQS.get(doc.value.u8)

    def _set_eq_preset(self, value):
        eqs = {v: k for k, v in self.EQS.items()}
        if value not in eqs:
            raise RuntimeError('Not allowed to set EQ to `%s`' % value)

        doc = self._call('SET/netRemote.sys.audio.eqPreset', dict(value=eqs.get(value)))
        return doc.status == 'FS_OK'

    eq_preset = property(_get_eq_preset, _set_eq_preset)

    def eq_custom(self, band, value=None):
        if type(value) is int:
            doc = self._call('SET/netRemote.sys.audio.eqCustom.param%s' % band, dict(
                value=value,
            ))
            return doc.status == 'FS_OK'

        doc = self._call('GET/netRemote.sys.audio.eqCustom.param%s' % band)
        return doc.value.s16
