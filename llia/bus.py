# llia.bus.py
# Defines abstract bus objects

from __future__ import print_function
import abc

from llia.generic import is_bus_source, is_bus_sink

class BusSource(object):

    '''
    Represents a bus source signal as synth_id and synth parameter.
    '''
    
    def __init__(self, sid, param):
        self.sid = sid
        self.param = param
        
    def __eq__(self, other):
        '''
        An object is considered eq to self if:
        1) other is self
        2) other is an instance of BusSource and at least one of the 
           following conditions is true:
           a) other.param == self.param
           b) other.param is '' or None
        '''
        if self is other:
            return True
        else:
            if not is_bus_source(other):
                return False
        if other.sid == self.sid:
            if not other.param:
                return True
            else:
                return other.param == self.param
        else:
            return False
            
    def __neq__(self, other):
        return not self.__eq__(other)

    def as_tuple(self):
        return tuple([self.sid, self.param])
    
    def __str__(self):
        s = 'BusSource("%s","%s")'
        return s % (self.sid, self.param)

@is_bus_source.when_type(BusSource)
def _is_bus_source(obj):
    return True
    

class BusSink(object):

    '''
    Represents a bus signal sink as synth_id and synth parameter.
    '''
    
    def __init__(self, sid, param):
        self.sid = sid
        self.param = param
        
    def __eq__(self, other):
        '''
        An object is considered eq to self if:
        1) other is self
        2) other is an instance of BusSink and at least one of the 
           following conditions is true:
           a) other.param == self.param
           b) other.param is '' or None
        '''
        if self is other:
            return True
        else:
            if not is_bus_sink(other):
                return False
        if other.sid == self.sid:
            if not other.param:
                return True
            else:
                return other.param == self.param
        else:
            return False
            
    def __neq__(self, other):
        return not self.__eq__(other)

    def as_tuple(self):
        return tuple([self.sid, self.param])
    
    def __str__(self):
        s = 'BusSink("%s","%s")'
        return s % (self.sid, self.param)

@is_bus_sink.when_type(BusSink)
def _is_sink(obj):
    return True
    

                   
class Bus(object):
    '''
    An abstract super class for audio or control buses.
    Each bus has a name, a list of sources and a list of sinks.
    '''
    def __init__(self, name):
        super(Bus, self).__init__()
        self.name = name
        self._sources = []
        self._sinks = []

    @abc.abstractmethod
    def is_protected(self):
        return False

    @abc.abstractmethod
    def rate(self):
        return None

    def is_audio_bus(self):
        return self.rate() == "Audio"

    def is_control_bus(self):
        return self.rate() == "Control"

    def has_source(self, sid, param=''):
        bs = BusSource(sid, param)
        for q in self._sources:
            if q == bs: return True
        return False
        
    def add_source(self, sid, param):
        if not self.has_source(sid, param):
            bs = BusSource(sid, param)
            self._sources.append(bs)

    def remove_source(self,sid, param=''):
        bs = BusSource(sid, param)
        def fn(a):
            return not(a == bs)
        self._sources = filter(fn, self._sources)

    def has_sink(self, sid, param=''):
        bs = BusSink(sid, param)
        for q in self._sinks:
            if q == bs: return True
        return False
        
    def add_sink(self, sid, param):
        if not self.has_sink(sid, param):
            bs = BusSink(sid, param)
            self._sinks.append(bs)

    def remove_sink(self,sid, param=''):
        bs = BusSink(sid, param)
        def fn(a):
            return not(a == bs)
        self._sinks = filter(fn, self._sinks)
            
    def dump(self, depth=0, silent=False):
        pad1 = ' '*4*depth
        pad2 = pad1 + ' '*4
        pad3 = pad2 + ' '*4
        r = self.rate()
        acc = "%s%sBus\n" % (pad1, r)
        acc += "%ssources:\n" % pad2
        for s in self._sources:
            t = s.as_tuple()
            acc += '%s%s\n' % (pad3, t)
        acc += "%ssinks:\n" % pad2
        for s in self._sinks:
            t = s.as_tuple()
            acc += '%s%s\n' % (pad3, t)
        if not silent:
            print(acc)
        return acc

    def __str__(self):
        frmt = '%sBus("%s")'
        return frmt % (self.rate(), self.name)
    
        
class AudioBus(Bus):

    def __init__(self, name):
        super(AudioBus, self).__init__(name)

    @staticmethod
    def rate():
        return "Audio"

    def is_protected(self):
        return self.name.startswith("out_") or self.name.startswith("in_")


class ControlBus(Bus):

    def __init__(self, name):
        super(ControlBus, self).__init__(name)

    @staticmethod
    def rate():
        return "Control"

    def is_protected(self):
        return self.name.startswith("CBUS")