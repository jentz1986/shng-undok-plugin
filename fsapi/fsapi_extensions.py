from .fsapi_exception import *
from .fsapi_node import *
from .netRemote_session import *  # noqa
from .netRemote_sys import *  # noqa
from .netRemote_sys_caps import *  # noqa
from .netRemote_sys_audio import *  # noqa
from .netRemote_play import *  # noqa


# Read-write ##################################################################################

def _get_vol_perc(self):
    vol = self.volume
    stp = self.volume_steps
    return int(100 * (vol / (stp-1)))


def _set_vol_perc(self, target_volume):
    stp = self.volume_steps
    vol = int(target_volume / 100 * (stp - 1))  # 21 steps = 0 ... 20!
    self.volume = vol


FSAPI.register_high_level_property('volume_percent', _get_vol_perc, _set_vol_perc,
                                   [FSAPI_Node_Volume, FSAPI_Node_Volume_Steps])

##############################################################################################


def _get_mode(self):
    modes = self.valid_modes
    mode = self.mode_key
    return next(iter([sm for sm in modes if sm['key'] == mode]), None)


def _set_mode(self, value):
    modes = self.valid_modes
    if value is int:
        hit_key = next(iter([sm['key'] for sm in modes if sm['key'] == value]), -1)
    elif isinstance(value, str):
        lval = value.lower()
        hit_key = next(iter([sm['key'] for sm in modes if sm['id'].lower() == lval]), -1)

    if hit_key == -1:
        raise RuntimeError('Not allowed to set mode to `%s`' % value)

    self.mode_key = hit_key


FSAPI.register_high_level_property('mode', _get_mode, _set_mode, [FSAPI_Node_Mode, FSAPI_Node_Valid_Modes])


################################################################################################


def _control_play(self):
    self.play_control = 'play'
FSAPI.register_proxy_method('control_play', _control_play, [FSAPI_Node_PlayControl])
    
def _control_paus(self):
    self.play_control = 'pause'
FSAPI.register_proxy_method('control_pause', _control_paus, [FSAPI_Node_PlayControl])

def _control_stop(self):
    self.play_control = 'stop'
FSAPI.register_proxy_method('control_stop', _control_stop, [FSAPI_Node_PlayControl])

def _control_next(self):
    self.play_control = 'next'
FSAPI.register_proxy_method('control_next', _control_next, [FSAPI_Node_PlayControl])

def _control_prev(self):
    self.play_control = 'previous'
FSAPI.register_proxy_method('control_previous', _control_prev, [FSAPI_Node_PlayControl])