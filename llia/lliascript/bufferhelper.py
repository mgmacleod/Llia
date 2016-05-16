# llia.lliascript.bufferhelper
# 2016.05.16
# Extends Parser with buffer related commands.
#

from __future__ import print_function

from llia.lliascript.ls_constants import *



class BufferHelper(object):

    def __init__(self, parser, local_namespace):
        self.parser = parser
        self.proxy = parser.proxy
        self.current_buffer = ""
        self._init_namespace(local_namespace)

    def _init_namespace(self, ns):
        ns["buffer"] = self.add_buffer
        ns["wavetab"] = self.create_wave_table
        ns["sinetab"] = self.create_sine_table
        ns["sawtab"] = self.create_wave_table
        ns["pulsetab"] = self.create_pulse_table
        ns["use_buffer"] = self.use_buffer

    def status(self, msg):
        self.parser.status(msg)

    def warning(self, msg):
        self.parser.warning(msg)

    def update_prompt(self):
        pass
        
    def buffer_exists(self, name=None):
        name = name or self.current_buffer
        blist = self.proxy.get_buffer_list()
        return name in blist

    def what_is(self, name):
        return self.parser.what_is(name)

    def use_buffer(self, name=None):
        name = name or self.current_buffer
        if self.buffer_exists(name):
            self.current_buffer = name
            msg = "Using buffer: %s" % name
            self.status(msg)
            self.update_prompt()
        else:
            raise NoSuchBufferError(name)
        
    def add_buffer(self, name, frames=1024, channels=1):
        if self.buffer_exists(name):
            self.use_buffer(name)
            return True
        flag = self.parser.register_entity(name, 
                                           "buffer",
                                           {"frames" : frames,
                                            "channels" : channels})
        if flag:
            rs = self.proxy.add_buffer(name, frames, channels)
            self.use_buffer(name)
            return rs
        else:
            return False
            
    def create_wave_table(self, name, harmonics=512, decay=0.5, skip=-1,
                         cutoff=-1, mode="", depth=0.5, frames=1024):
        xtype = self.what_is(name)
        if xtype:
            msg = "%s entity '%s' already exists, can not create wavetable with same name"
            msg = msg % (xtype, name)
            self.warning(msg)
            return False
        else:
            if skip == -1: skip = harmonics+1
            if cutoff == -1: cutoffer = harmonics/2
            self.proxy.create_wavetable(name, harmonics, decay, skip, mode, cutoff, depth, frames)
            self.parser.register_entity(name,
                                        "buffer",
                                        {"frames" : frames,
                                         "channels" : 1})
            self.use_buffer(name)
            return True
        
    def create_sine_table(self, name, frames=1024):
        return self.create_wave_table(name, 1, frames=frames)

    def create_pulse_table(self, name, harmonics=512, skip=2, frames=1024):
        if skip <= 1:
            decay = 0
            skip = harmonics+1
        else:
            decay = 1
        return self.create_wave_table(name, harmonics, decay, skip, frames=frames)
    
