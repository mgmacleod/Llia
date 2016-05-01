# llia.proxy
# 2016.04.20
#

from __future__ import print_function
from time import sleep

from llia.osc_transmitter import OSCTransmitter
from llia.osc_receiver import OSCReceiver
from llia.synth_proxy import SynthSpecs
from llia.generic import is_int

class LliaProxy(object):

    trace = False
    
    def __init__(self, config, app):
        self.config = config
        self.app = app
        osc_trace = config.osc_transmission_trace_enabled()
        self.osc_transmitter = OSCTransmitter(self.global_osc_id(), self.osc_host(), osc_trace)
        caddress, cport  = config["client"], config["client_port"]
        self.osc_receiver = OSCReceiver(self.global_osc_id(), caddress, cport)
        self.synths = {}

        # Keep track of allocated proivate audio buses.
        # _first_private_audio_bus is initially set to a default but
        # should be updated by polling the sc server by calling
        # self.q_bus_and_buffer_info()
        # The value _private_audio_bus_counter is incremented
        # as busses are added and is relative to the first private value.
        #
        # Entries in _audio_buses dictionary are tuples
        # (Alias, bus_index, numer_channels)
        #
        # ISSUE: Llia does not keep track of buses or buffers which are created
        # by external processes.  If an audio_bus, control_bus or buffer
        # is created by some external to Llia then indexing to these objects
        # from Llia will fail!!!!
        #
        self._first_private_audio_bus = 16
        self._private_audio_bus_counter = 0 
        self._control_bus_counter = 0
        self._audio_buses = {}
        self._control_buses = {}
        self._callback_message = {}
        self.osc_receiver.add_handler("llia-ping-response", self._expect_response)
        self.osc_receiver.add_handler("llia-dump-response", self._expect_response)
        self.osc_receiver.add_handler("set-llia-client", self._expect_response)
        self.osc_receiver.add_handler("llia-keymodes", self._expect_response)
        self.osc_receiver.add_handler("llia-synthtypes", self._expect_response)

        self.osc_receiver.add_handler("llia-audio-buses", self._expect_response)
        self.osc_receiver.add_handler("audio-bus-info", self._expect_response)
        
        self.osc_receiver.add_handler("llia-control-buses", self._expect_response)
        self.osc_receiver.add_handler("control-bus-info", self._expect_response)
        
        self.osc_receiver.add_handler("llia-added-synth", self._expect_response)
        self.osc_receiver.add_handler("llia-active-synths", self._expect_response)
        self.osc_receiver.add_handler("all-running-servers", self._expect_response)
        self.osc_receiver.add_handler("llia-booting-server", self._expect_response)
        self.osc_receiver.add_handler("llia-server-quit", self._expect_response)
        self.osc_receiver.add_handler("llia-kill-all-servers", self._expect_response)
        
        self.osc_receiver.add_handler("ERROR", self._expect_response)

        

    def _expect_response(self, path, tags, args, source):
        self._callback_message = {"path" : path,
                                  "tags" : tags,
                                  "args" : args,
                                  "source" : source}

    def warning(self, msg):
        self.app.warning(msg)
    
    def global_osc_id(self):
        return self.config.global_osc_id()

    def osc_host(self):
        return self.config["host"], self.config["port"]

    # Returns dictionary from current callback
    # The callback dictionary may only be read once.
    # Once read the dictionary contents are cleared.
    #
    def _get_callback_message(self):
        rs = self._callback_message.copy()
        self._callback_message = {}
        return rs

    # Check callback dictionary for expected response message
    # Return True if expected message has been received.
    # Return False otherwise
    #
    def _expect(self, msg):
        rs = False
        try:
            sleep(0.05)
            self.osc_receiver.handle_request()
            cbm = self._get_callback_message()
            msg = "/Llia/%s/%s" % (self.global_osc_id(), msg)
            rs = msg == cbm["path"]
        except KeyError:
            wmsg = "Did not receive expected response: '%s'" % msg
            self.warning(wmsg)
        finally:
            return rs

    # Transmit OS message
    # msg - /oscID/msg
    # payload - optional data
    #
    def _send(self, msg, payload=[]):
        if LliaProxy.trace:
            # print("send '%s' %s" % (msg, payload))
            self.app.status("LliaProxy._send '%s' %s" % (msg, payload))
        self.osc_transmitter.send(msg, payload)

    # Request host to return value(s)
    # msg - /oscID/msg
    # returns -> list
    def _query_host(self, msg, delim=" "):
        self._send(msg)
        self.osc_receiver.handle_request()
        cbm = self._get_callback_message()
        args = cbm.get("args", [""])
        args = args[0].split(delim)
        return args

    # Request list of bus aliases
    # msg - /oscID/msg
    # returns -> list
    def _query_bus_names(self, msg):
        self._send(msg)
        self.osc_receiver.handle_request()
        cbm = self._get_callback_message()
        args = cbm.get("args", [""])[0]
        args = str(args).strip()
        args = args.split(" ")
        if args == ['']: args = []
        return args
    
    def q_keymodes(self):
        km = self._query_host("query-keymodes")
        self.app.log_event("keymodes: %s" % km)
        return km

    def q_synthtypes(self):
        st = self._query_host("query-synthtypes")
        self.app.log_event("synthtypes: %s" % st)
        return st

    def q_bus_and_buffer_info(self):
        st = self._query_host("query-bus-and-buffer-info")
        if st == ['']:
            return False
        else:
            info = {"audio-bus-count" : int(st[0]),
                    "output-buses" : int(st[1]),
                    "input-buses" : int(st[2]),
                    "first-private-bus" : int(st[3]),
                    "control-bus-count" : int(st[4]),
                    "buffer-count" : int(st[5])}
            self._first_private_audio_bus = info["first-private-bus"]
            return info
    
    def q_audio_buses(self):
        b = self._query_bus_names("query-audio-buses")
        self.app.log_event("audio buses: %s" % b)
        return b

    def q_audio_bus_info(self, bus_id):
        self._send("audio-bus-info", [str(bus_id)])
        self.osc_receiver.handle_request()
        cbm = self._get_callback_message()
        args = cbm.get("args", [""])
        args = args[0].strip().split(" ")
        flag = args[1].upper() == "TRUE"
        rate = args[2]
        if flag:
            index = int(args[3])
            channels = int(args[4])
        else:
            index = None
            channels = None
        return {"id": bus_id,
                "flag" : flag,
                "rate" : rate,
                "index" : index,
                "channels" : channels}
    
    def q_control_buses(self):
        b = self._query_bus_names("query-control-buses")
        self.app.log_event("control buses: %s" % b)
        return b

    def q_control_bus_info(self, bus_id):
        self._send("control-bus-info", [str(bus_id)])
        self.osc_receiver.handle_request()
        cbm = self._get_callback_message()
        args = cbm.get("args", [""])
        args = args[0].strip().split(" ")
        flag = args[1].upper() == "TRUE"
        rate = args[2]
        if flag:
            index = int(args[3])
            channels = int(args[4])
        else:
            index = None
            channels = None
        return {"id": bus_id,
                "flag" : flag,
                "rate" : rate,
                "index" : index,
                "channels" : channels}
    
    # Request server be booted.
    # s : {"local", "internal", "default"}
    # and wait 2 seconds.
    #
    def boot_server(self, s="default"):
        self._send("boot-server", [s])
        sleep(2)
        return self._expect("llia-booting-server")

    # Returns list of all running server names.
    #
    def q_running_servers(self):
        self._send("query-all-running-servers")
        self.osc_receiver.handle_request()
        cbm = self._get_callback_message()
        servers = cbm.get("args", [""])[0].strip().split(" ")
        if servers == ['']:
            servers = []
        return servers

    def quit_server(self, s="default"):
        self._send("quit-server", s)
        return self._expect("llia-server-quit")

    def kill_all_servers(self):
        self._send("kill-all-servers")
        return self._expect("llia-kill-all-servers")
    
    def ping(self):
        self._send("ping")
        return self._expect("llia-ping-response")

    def dump(self):
        self._send("dump")
        #print(self.dump())
        return self._expect("llia-dump-response")

    def post_message(self, text):
        self._send("post", text)

    def set_client(self):
        ip, port = self.config["client"], self.config["client_port"]
        self._send("set-llia-client", [ip, port])
        return self._expect("set-llia-client")

    def audio_bus_exists(self, name):
        return (is_int(name) and int(name) >= 0) or\
            self._audio_buses.has_key(name)
    
    def add_audio_bus(self, name, numchan=1):
        if self._audio_buses.has_key(name):
            msg = "Audio bus '%s' already exists" % name
            self.warning(msg)
            return False
        else:
            self._send("add-audio-bus", [name, numchan])
            rs = self._expect("llia-audio-buses")
            index = self._first_private_audio_bus +\
                    self._private_audio_bus_counter
            data = (name, index, numchan)
            if rs:
                self._audio_buses[name] = data
                self._private_audio_bus_counter += numchan
                return True
            else:
                msg = "Audio bus '%s' could not be created" % name
                self.warning(msg)
                return False

    def get_audio_bus_index(self, name, offset=0):
        if is_int(name):
            bi = int(name)
        else:
            info = self._audio_buses[name]
            bi = info[1]
        return bi+int(offset)
        
    def add_control_bus(self, name, numchan=1):
        if self._control_buses.has_key(name):
            msg = "Control bus '%s' already exists" % name
            self.warning(msg)
            return False
        else:
            self._send("add-control-bus", [name, numchan])
            rs = self._expect("llia-control-buses")
            # index = self._first_private_control_bus +\
            #         self._private_control_bus_counter
            index = self._control_bus_counter
            data = (name, index, numchan)
            if rs:
                self._control_buses[name] = data
                self._control_bus_counter += numchan
                return True
            else:
                msg = "Control bus '%s' could not be created" % name
                self.warning(msg)
                return False

    def get_control_bus(self, name, offset=0):
        if is_int(name):
            bi = int(name)
        else:
            info = self._control_buses[name]
            bi = info[1]
        return bi+int(offset)

    
    # def add_control_bus(self, name, numchan=1):
    #     if self.control_buses.has_key(name):
    #         msg = "Control bus '%s' already exists" % name
    #         self.warning(msg)
    #         return False
    #     else:
    #         self._send("add-control-bus", [name, numchan])
    #         rs = self._expect("llia-control-buses")
    #         if rs:
    #             self.control_buses[name] = numchan
    #             return True
    #         else:
    #             msg = "Control bus '%s' could not be created" % name
    #             self.warning(msg)
    #             return False

    def add_synth(self, synthType, oscID, keymode="Poly1",
                  outbus=(0,0),      # (alias, offset)
                  inbus=(1000, 0),   # (alias, offset)
                  voice_count=8):
        if not SynthSpecs.is_known_synth_type(synthType):
            msg = "Unknown synth type: '%s'" % synthType
            self.warning(msg)
            return False
        key = "%s_%s" % (synthType, oscID)
        if self.synths.has_key(key):
            msg = "Synth /Llia/%s/%s/%s already exists" % (self.app.global_osc_id(), synthType, oscID)
            self.warning(msg)
            return False
        obi = self.get_audio_bus_index(outbus[0], outbus[1])
        ibi = self.get_audio_bus_index(inbus[0], inbus[1])
        self._send("add-synth", [synthType, oscID, keymode, obi, ibi, voice_count])
        rs = self._expect("llia-added-synth")
        if rs:
            info = {"synthType" : synthType,
                    "oscID" : oscID,
                    "keyMode" : keymode,
                    "outbus" : outbus,
                    "inbus" : inbus,
                    "voice_count" : voice_count}
            spec = SynthSpecs.global_synth_type_registry[synthType]
            sproxy = spec.create_proxy_synth(self.app)
            sproxy.info = info
            self.synths[key] = sproxy
            return sproxy
        else:
            msg = "Synth /Llia/%s/%s/%s could not be added" % (self.app.global_osc_id(), synthType, oscID)
            self.warning(msg)
            return False

    def add_efx(self, synthType, oscID, inbus, outbus=(0, 0)):
        # inbus a tuple (index,offset)
        s = self.add_synth(synthType, oscID, "EFX", outbus, inbus, 1)
        if s: s.is_efx = True
        return s 

    def q_active_synths(self):
        slt = self._query_host("query-active-synths", delim="<synth>")
        if slt == [""]:
            slt = []
        else:
            for s in slt:
                if s != '':
                    s = s.strip()
                    self.app.log_event("    %s" % s)
        return slt
