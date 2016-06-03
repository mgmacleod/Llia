# llia.gui.tk.tk_appwindow
# 2016.05.20

from __future__ import print_function
from Tkinter import (Frame, Label, Menu, Tk, BOTH, Toplevel)
import ttk
import tkMessageBox
from PIL import Image, ImageTk
from llia.gui.tk.tk_help import TkHelpDialog
from llia.gui.appwindow import AbstractApplicationWindow
from llia.gui.tk.tk_splash import TkSplashWindow
import llia.gui.tk.tk_factory as factory
import llia.gui.tk.tk_layout as layout
from  llia.proxy import LliaProxy

class TkApplicationWindow(AbstractApplicationWindow):

    def __init__(self, app):
        self.root = Tk()
        self.root.title("Llia")
        #self.root.configure(background=factory.pallet["BG"])
        super(TkApplicationWindow, self).__init__(app, self.root)
        self.root.withdraw()
        if app.config["enable-splash"]:
            splash = TkSplashWindow(self.root, app)
        self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self._main = layout.BorderFrame(self.root)
        self._main.pack(anchor="nw", expand=True, fill=BOTH)
        self._init_status_panel()
        self._init_menu()
        self.root.minsize(width=665, height=375)
        self._help_dialog = TkHelpDialog(self.root)
        self._help_dialog.withdraw()
        
    def _init_status_panel(self):
        south = self._main.south
        south.configure(padx=4, pady=4)
        self._lab_status = factory.label(south, "")
        b_panic = factory.button(south, "PANIC")
        ttip = "Clear status line"
        b_clear_status = factory.clear_button(south,command=self.clear_status,ttip=ttip)
        b_panic.grid(row=0, column=0, sticky="w")
        b_clear_status.grid(row=0, column=1, sticky="w")
        self._lab_status.grid(row=0,column=2, sticky="w", ipadx=8) 

    @staticmethod
    def menu(master):
        m = Menu(master, tearoff=0)
        #m.configure(background=factory.pallet["BG"])
        #m.configure(foreground=factory.pallet["FG"])
        return m
    
    def _init_menu(self):
        main_menu = self.menu(self.root)
        self.root.config(menu=main_menu)
        file_menu = self.menu(main_menu)
        osc_menu = self.menu(main_menu)
        midi_menu = self.menu(main_menu)
        bus_menu = self.menu(main_menu)
        buffer_menu = self.menu(main_menu)
        synth_menu = self.menu(main_menu)
        tune_menu = self.menu(main_menu)
        help_menu = self.menu(main_menu)
        main_menu.add_cascade(label="File", menu=file_menu)
        main_menu.add_cascade(label="OSC", menu=osc_menu)
        main_menu.add_cascade(label="MIDI", menu=midi_menu)
        main_menu.add_cascade(label="Buses", menu=bus_menu)
        main_menu.add_cascade(label="Buffers", menu=buffer_menu)
        main_menu.add_cascade(label="Synths", menu=synth_menu)
        main_menu.add_cascade(label="Tune", menu=tune_menu)
        main_menu.add_cascade(label="Help", menu=help_menu)
        self._init_file_menu(file_menu)
        self._init_osc_menu(osc_menu)
        self._init_midi_menu(midi_menu)
        self._init_bus_menu(bus_menu)
        self._init_buffer_menu(buffer_menu)
        self._init_synth_menu(synth_menu)
        self._init_tune_menu(tune_menu)
        self._init_help_menu(help_menu)

    def _init_file_menu(self, fmenu):
        fmenu.add_command(label="Lliascript", command = self.show_history_editor)
        fmenu.add_separator()
        fmenu.add_command(label="Quit", command = self.exit_app)

    def _init_osc_menu(self, iomenu):
        iomenu.add_command(label="Ping", command = self.ping_global)
        iomenu.add_command(label="Dump", command = self.app.proxy.dump)
        iomenu.add_command(label="Toggle OSC Trace", command = self.toggle_osc_trace)

    def _init_midi_menu(self, mmenu):
        map_menu = self.menu(mmenu)
        mmenu.add_command(label = "Channel Names", command = self.show_channel_name_dialog)
        mmenu.add_command(label = "Controller Names", command = self.show_controller_name_dialog)
        mmenu.add_cascade(label = "MIDI Maps", menu = map_menu)
        mmenu.add_command(label = "Toggle MIDI Input Trace", command = self.toggle_midi_input_trace)
        mmenu.add_command(label = "Toggle MIDI Output Trace", command = self.toggle_midi_output_trace)
        
    def _init_bus_menu(self, bmenu):
        bmenu.add_command(label="Audio", command=self.show_audiobus_dialog)
        bmenu.add_command(label="Control", command=self.show_controlbus_dialog)
        
    def _init_buffer_menu(self, bmenu):
        bmenu.add_command(label="View Buffers", command=self.show_bufferlist_dialog)
        bmenu.add_command(label="Edit Buffers", command = None)
        
    def _init_synth_menu(self, smenu):
        smenu.add_command(label = "Show Synth", command = None)
        smenu.add_command(label = "Hide Synth", command = None)
        smenu.add_separator()
        smenu.add_command(label = "Add Synth", command = None)
        smenu.add_command(label = "Add EFX Synth", command = None)
        smenu.add_command(label = "Remove Synth", command = None)

    def _init_tune_menu(self, tmenu):
        tmenu.add_command(label = "FIX ME: Nothing to see here")

    def _init_help_menu(self, hmenu):
        hmenu.add_command(label = "About", command = self.show_about_dialog)
        hmenu.add_command(label = "Help", command = self.show_help_dialog)
    
        
    def exit_gui(self):
        try:
            self.root.destroy()
        except:
            pass

    def exit_app(self):
        # ISSUE: Check config and ask user confirmation before existing
        self.app.exit_()

    def as_widget(self):
        return self.root
        
    def status(self, msg):
        self._lab_status.config(text=str(msg))

    def warning(self, msg):
        msg = "WARNING: %s" % msg
        self._lab_status.config(text=msg)
        
    def clear_status(self):
        self.status("")
                                              
    def start_gui_loop(self):
        self.root.mainloop()

    def show_about_dialog(self):
        from llia.gui.tk.tk_about_dialog import TkAboutDialog
        dialog = TkAboutDialog(self.root, self.app)
        self.root.wait_window(dialog)

    def show_help_dialog(self, topic=None):
        if topic:
            self._help_dialog.display_topic(topic)
        self._help_dialog.deiconify()
        
    def show_history_editor(self):
        from llia.gui.tk.tk_history import TkHistoryEditor
        dialog = TkHistoryEditor(self.root, self.app)
        self.root.wait_window(dialog)

    def ping_global(self):
        rs = self.app.proxy.ping()
        if rs:
            self.status("Ping OK")
        else:
            self.warning("No Ping Response")

    def toggle_osc_trace(self):
        LliaProxy.trace = not LliaProxy.trace
        if LliaProxy.trace:
            self.status("OSC transmission trace enabled")
        else:
            self.status("OSC transmission trace disabled")

    def show_channel_name_dialog(self):
        from llia.gui.tk.tk_channel_name_editor import TkChannelNameEditor
        dialog = TkChannelNameEditor(self.root, self.app)
        self.root.wait_window(dialog)
  
    def show_controller_name_dialog(self):
        from llia.gui.tk.tk_controller_name_editor import TkControllerNameEditor
        dialog = TkControllerNameEditor(self.root, self.app)
        self.root.wait_window(dialog)
    
    def toggle_midi_input_trace(self):
        flag = not self.app.midi_in_trace
        self.app.midi_in_trace = flag
        self.app.midi_receiver.enable_trace(flag)
        if flag:
            self.status("MIDI input trace enabled")
        else:
            self.status("MIDI output trace disabled")

    def toggle_midi_output_trace(self):
        self.status("MIDI output not available") # FIX ME

    def show_audiobus_dialog(self):
        from llia.gui.tk.tk_audiobus_editor import TkAudiobusEditor
        dialog = TkAudiobusEditor(self.root, self.app)
        self.root.wait_window(dialog)

    def show_controlbus_dialog(self):
        from llia.gui.tk.tk_controlbus_editor import TkControlbusEditor
        dialog = TkControlbusEditor(self.root, self.app)
        self.root.wait_window(dialog)

    def show_bufferlist_dialog(self):
        from llia.gui.tk.tk_buffer_info import TkBufferListDialog
        dialog = TkBufferListDialog(self.root, self.app)
        self.root.wait_window(dialog)