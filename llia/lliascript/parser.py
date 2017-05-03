# llia.lliascript.parser
# 2016.05.14

from __future__ import print_function
import sys, os.path, json

from llia.lliascript.ls_constants import *
from llia.llerrors import (LliaPingError, LliascriptParseError,
                           LliascriptError,NoSuchBusError)
from llia.lliascript.ls_command import LsCommand
from llia.lliascript.synthhelper import SynthHelper
from llia.lliascript.graphhelper import GraphHelper
from llia.lliascript.compose import Composer
from llia.lliascript.scene import Scene
import llia.constants as con

class LsEntity(object):

    def __init__(self, lsid, lstype):
        self.lsid = lsid
        self.lstype = lstype
        self.data = {}

    def __repr__(self):
        acc = "LsEntity(lsid='%s', lstype='%s')\n" % (self.lsid, self.lstype)
        for k in sorted(self.data.keys()):
            v = self.data[k]
            acc += "   [%-12s] : %s\n" % (k, v)
        acc += '\n'
        return acc
        
class Parser(object):

    def __init__(self, app):
        self.app = app
        self.proxy = app.proxy
        self.config = app.config
        self.exit_repl = False
        self._prompt = "Llia> "
        self.entities = {}
        # Default audio buses
        # ISSUE: Number of private input and output buses is hard coded.
        #
        for i in range(8):
            for n in ("out_", "in_"):
                name = "%s%d" % (n, i)
                e = LsEntity(name, "abus")
                self.entities[name] = e
        # Default control buses
        #
        name = "null_source"
        e = LsEntity(name, "cbus")
        self.entities[name] = e
        name = "null_sink"
        e = LsEntity(name, "cbus")
        self.entities[name] = e
        
        self._history = ""
        self._global_namespace = {}
        self._local_namespace = {}
        self._lsCommand = LsCommand(self)
        self.synthhelper = SynthHelper(self, self._local_namespace)
        #self.bufferhelper = BufferHelper(self, self._local_namespace)
        self.graphhelper = GraphHelper(self, self._local_namespace)
        self._init_namespace(self._local_namespace)


    def _init_namespace(self, ns):
            ns["app"] = self.app
            ns["config"] = self.config
            ns["proxy"] = self.proxy
            ns["ABUS"] = ABUS
            ns["CBUS"] = CBUS
            #ns["BUFFER"] = BUFFER
            ns["SYNTH"] = SYNTH
            ns["EFX"] = EFX
            ns["CHAN"] = CHAN
            ns["CTRL"] = CTRL
            ns["STYPE"] = STYPE
            ns["KEYMODE"] = KEYMODE
            ns["ALL"] = ALL
            ns["velocity"] = velocity
            ns["aftertouch"] = aftertouch
            ns["keynumber"] = keynumber
            ns["pitchwheel"] = pitchwheel
            ns["linear"] = linear
            ns["exp"] = exp
            ns["scurve"] = scurve
            ns["step"] = step
            ns["apropos"] = self.apropos
            ns["help"] = self.help_
            ns["abus"] = self.abus
            ns["compose"] = self.compose
            ns["cbus"] = self.cbus
            ns["channel_name"] = self.channel_name
            ns["controller_name"] =self.controller_name
            ns["clear_history"] = self.clear_history
            ns["dump"] = self.dump
            ns["history"] = self.print_history
            ns["ls"] = self._lsCommand.ls
            ns["panic"] = self.panic
            ns["ping"] = self.ping
            ns["pp"] = self.pretty_printer
            ns["batch"] = self.load_python
            ns["rm"] = self.rm
            ns["sync"] = self.sync_all
            ns["trace_midi"] = self.trace_midi
            ns["trace_osc"] = self.trace_osc
            ns["what_is"] = self.what_is_interactive
            ns["exit"] = self.exit_
            ns["test"] = self.test
            ns["save_scene"] = self.save_scene
            ns["load_scene"] = self.load_scene
            ns["tabula_rasa"] = self.tabula_rasa
        
    def repl(self):
        print(BANNER)
        print()
        pyver = sys.version_info[0]
        if pyver <= 2:
            infn = raw_input
        else:
            infn = input
        while not self.exit_repl:
            usrin = infn(self._prompt)
            self._append_history(usrin, False)
            try:
                self.batch(usrin)
            except SyntaxError as err:
                msg = "SyntaxError: %s" % err.message
                print(msg)
                self._append_history(msg)
            except NameError as err:
                msg = "NameError: %s" % err.message
                print(msg)
                self._append_history(msg)
            #self.proxy.sync_to_host()
                
    def batch(self, pycode):
        try:
            exec pycode in self._global_namespace, self._local_namespace
        except Exception as err:
            msg = "%s " % err.__class__.__name__
            self.warning(msg)
            self.warning(err.message)

    def load_python(self, filename):
        fname = os.path.expanduser(filename)
        if os.path.exists(fname):
            with open(fname, 'r') as input:
                pycode = input.read()
                self.batch(pycode)
            return True
        else:
            msg = "Can not open python file '%s' for input" % fname
            self.warning(msg)
            return False
        
    def _append_history(self, text, as_remark=True):
        if as_remark: text = "# " + text
        self._history += "%s\n" % text
        
    def warning(self, msg):
        for line in str(msg).split("\n"):
            line = "WARNING: %s" % line
            print(line)
            self._append_history(line)

    def status(self, msg):
        for line in str(msg).split("\n"):
            print(line)
            self._append_history(line)

    def help_(self, topic=None):
        print("lliascript help not implemented")

    def apropos(self, target):
        print("lliascript apropos not implemented")
            
    def is_abus(self, name):
        ent = self.entities.get(name, None)
        return ent and ent.lstype == "abus"

    def is_cbus(self, name):
        ent = self.entities.get(name, None)
        return ent and ent.lstype == "cbus"

    # def is_buffer(self, name):
    #     ent = self.entities.get(name, None)
    #     return ent and ent.lstype == "buffer"

    def is_synth(self, name):
        ent = self.entities.get(name, None)
        return ent and ent.lstype == "synth"

    def is_channel(self, name):
        try:
            name = int(str(name))
            return 1 <= name <= 16
        except ValueError:
            return self.config.channel_assignments.channel_defined(name)

    def is_controller(self, name):
        try:
            ctrl = int(str(name))
            return 0 <= ctrl <= 127
        except ValueError:
            return self.config.controller_assignments.controller_defined(name)

    # Removes name from parser entities only.
    # Does not actually remove underlying object.
    #
    def forget(self, name):
        try:
            del self.entities[name]
        except KeyError:
            pass

        
        
    def what_is(self, name):
        ent = self.entities.get(name, None)
        if ent:
            return ent.lstype
        else:
            chnflag = self.is_channel(name)
            ccflag = self.is_controller(name)
            if chnflag and ccflag:
                return "channel_or_controller"
            else:
                if chnflag:
                    return "channel"
                if ccflag:
                    return "controller"
                return ""

    def what_is_interactive(self, name):
        lstype = self.what_is(name)
        if not lstype:
            msg = "'%s' is " % type(name)
        else:
            msg = "'%s' is a %s" % (name, lstype)
        self.status(msg)
        return lstype
        
    def register_entity(self, name, lstype, data = {}):
        xtype = self.what_is(name)
        if xtype and xtype != lstype:
            msg = "Can not change %s '%s' to %s"
            msg = msg % (xtype, name, lstype)
            self.warning(msg)
            return False
        else:
            ent = LsEntity(name, lstype)
            ent.data = data
            self.entities[name] = ent
            return True

    def abus(self, name):
        lstype = self.register_entity(name, "abus", {"channels" : 1})
        if lstype:
            if self.proxy.audio_bus_exists(name):
                msg = "Reusing existing audio bus '%s'" % name
                print(msg)
            else:
                self.proxy.add_audio_bus(name)
            return self.proxy.get_audio_bus(name)
        else:
            return False

    def cbus(self, name):
        lstype = self.register_entity(name, "cbus", {"channels" : 1})
        if lstype:
            if self.proxy.control_bus_exists(name):
                msg = "Reusing existing control bus '%s'" % name
                print(msg)
            else:
                self.proxy.add_control_bus(name)
            return self.proxy.get_control_bus(name)
        else:
            return False

    def _set_channel_name(self, channel, new_name):
        new_name.replace(' ','_')
        stype = self.what_is(new_name)
        if not stype:
            self.config.channel_name(channel, new_name)
        elif stype == "channel":
            old_chan = self.config.channel_number(new_name)
            if old_chan == channel:
                pass
            else:
                msg = "Channel '%s' already in use" % new_name
                raise ValueError(msg)
        else:
            msg = "Can not resuse %s '%s' as MIDI channel name"
            msg = msg % (stype, new_name)
            raise ValueError(msg)
    
    def channel_name(self, n, new_name=None, silent=False):
        if new_name != None:
            self._set_channel_name(n, new_name)
        cname = self.config.channel_name(n)
        if not silent: print(cname)
        return cname
    
    def _set_controller_name(self, ctrl, new_name):
        stype = self.what_is(new_name)
        if not stype:
            self.config.controller_name(ctrl, new_name)
        elif stype == "controller":
            old_ctrl = self.config.controller_assignments.get_controller_number(new_name)
            if old_ctrl == ctrl:
                pass
            else:
                if new_name == '':
                    self.config.controller_name(ctrl, '')
                else:
                    msg = "Controller name '%s' already in use" % new_name
                    raise ValueError(msg)
        else:
            msg = "Can not reuse %s '%s' as MIDI controller name"
            msg = msg % (stype, new_name)
            raise ValueError(msg)
    
    def controller_name(self, ctrl, new_name=None, silent=False):
        if 0 <= ctrl <= 127:
            if new_name != None:
                self._set_controller_name(ctrl, new_name)
            cname = self.config.controller_name(ctrl)
            if not silent: print(cname)
            return cname
        else:
            msg = "Illegal MIDI controller number: %s" % ctrl
            raise IndexError(msg)

    def clear_history(self):
        self._history = ""
        return True

    def get_history(self):
        return self._history

    def set_history(self, txt):
        self._history = txt
    
    def print_history(self):
        print("HISTORY:")
        print(self._history)
        return True

    # ISSUE: FIX ME dump target not implemented
    #
    def dump(self, target=None):
        if not target:
            self.proxy.dump()
        else:
            self.synthhelper.dump_synth(target)
            
    def panic(self):
        self.proxy.panic()
        print("Panic!")
        return True

    def ping(self, sid=None):
        try:
            if sid:
                self.synthhelper.ping_synth(sid)
                return True
            else:
                rs = self.proxy.ping()
                return rs
        except LliaPingError as err:
            self._append_history(err.message)
            print(err.message)
            return False
            
    def sync_all(self):
        # ISSUE: Broken app.sync_all not implemented.
        self.app.sync_all()
        return True
        
    def exit_(self):
        self.exit_repl = True
        self.app.exit_()

    def pretty_printer(self, flag=None):
        if flag is not None:
            if flag:
                flag = True
            else:
                flag = False
            self.config.set_option("MIDI", "enable-program-pp", flag)
        flag = self.config.get_option("MIDI", "enable-program-pp")
        msg = "Pretty printer "
        if flag:
            msg += "enabled."
        else:
            msg += "disabled."
        print(msg)
        return flag

    def trace_midi(self, flag):
        self.app.midi_receiver.enable_trace(flag)
        msg = "MIDI trace "
        if flag:
            msg += "enabled."
        else:
            msg += "disabled."
        print(msg)
        return flag
        
    def trace_osc(self, flag):
        self.proxy.osc_transmitter.trace = flag
        for sy in self.proxy.get_all_synths():
            sy.osc_transmitter.trace = flag
        msg = "Trace OSC "
        if flag:
            msg += "enabled."
        else:
            msg += "disabled."
        print(msg)
        return flag

    # DEPRECIATED bus removal
    # def remove_bus(self, name):
    #     lstype = self.what_is(name)
    #     if lstype == "abus":
    #         self.proxy.remove_audio_bus(name)
    #         self.forget(name)
    #         print("Removed audio bus: '%s'" % name)
    #     elif lstype == "cbus":
    #         self.proxy.remove_control_bus(name)
    #         self.forget(name)
    #         print("Removed control bus: '%s'" % name)
    #     else:
    #         raise NoSuchBusError(name)

    # Universal remove  (bus, synth, map)
    def rm(self, name, param=ALL, sid=None, force=False):
        lstype = self.what_is(name)
        if lstype == "abus" or lstype == "cbus":
            msg = "Buses can not be removed"
            raise LliascripError(msg)
        elif lstype == "synth" or lstype == "efx":
            self.synthhelper.remove_synth(name, force)
        elif "controller" in lstype:
            self.synthhelper.remove_parameter_map(name, param, sid)
        elif name in (velocity,aftertouch,keynumber,pitchwheel):
            self.synthhelper.remove_parameter_map(name, param, sid)
        else:
            msg = "Can not remove '%s' (type '%s')" % (name,lstype)
            raise LliascriptError(msg)

    def compose(self):
        rb = Composer(self)
        code = rb.build()
        self._history = code
        print(code)

    def save_scene(self, filename):
        scene = Scene(self)
        s = scene.serialize()
        self.status("Saving scene file '%s'" % filename)
        with open(filename,'w') as output:
            json.dump(s, output, indent=4)
        self.status("Scene saved to '%s'" % filename)
        
    def load_scene(self, filename):
        self.tabula_rasa()
        self.app.main_window().busy(True, "Loading scene '%s'" % filename)
        scene = Scene(self)
        with open(filename, 'r') as input:
            jobj = json.load(input)
            script = jobj["script"]
            self.batch(script)
            banks = jobj["bank_data"]
            self.app.main_window().busy(False)
            for sid,bnkdata in banks.items():
                sy = self.synthhelper.get_synth(sid)
                bank = sy.bank()
                bank.copy_bank(bank.deserialize(bnkdata, self.app.main_window()))
                slot = jobj["current_slots"][sid]
                locked = jobj["bank_locks"][sid]
                self.synthhelper.use_program(slot,sid)
                self.synthhelper.lock_bank(locked)
                try:
                    bed = sy.synth_editor.bank_editor
                    bed.sync_no_propegate()
                except AttributeError:
                    # Bank editor does not exists,
                    # Probably running without active GUI.
                    pass
                
        self.app.main_window().busy(False)
        self.status("Scene '%s' loaded" % filename)
        
    def tabula_rasa(self):
        self.app.tabula_rasa()
        self.entities = {}
        for i in range(con.PROTECTED_AUDIO_OUTPUT_BUS_COUNT):
            self.register_entity("out_%s" % i, "abus", {"channels" : 1})
        for i in range(con.PROTECTED_AUDIO_INPUT_BUS_COUNT):
            self.register_entity("in_%s" % i, "abus", {"channels" : 1})
        self.register_entity("null_sink", "cbus", {"channels" : 1})
        self.register_entity("null_source", "cbus", {"channels" : 1})
        self.synthhelper.new_group()
        self.synthhelper.show_group()
        
    def test(self):
        print("Lliascript entities")
        for k,v in self.entities.items():
            print("[%-16s] -> %s" % (k,v))
