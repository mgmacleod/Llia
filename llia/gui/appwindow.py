# llia.gui.appwindow
# 2016.04.23
#

from __future__ import print_function
import abc, sys

from llia.gui.splash import TextSplashScreen

class AbstractGroupWindow(object):

    def __init__(self, app, root=None, name=""):
        self.app = app
        self.root=root
        self.name = str(name)
        
    @abc.abstractmethod
    def on_closing(self, *args):
        pass

    @abc.abstractmethod
    def show_synth_editor(self, sid):
        pass

    @abc.abstractmethod
    def lift(self):
        pass

    @abc.abstractmethod
    def deiconify(self):
        pass
    
    @abc.abstractmethod
    def lower(self):
        pass

    @abc.abstractmethod
    def tabula_rasa(self):
        pass

    @abc.abstractmethod
    def sync(self):
        pass
    

    

class AbstractApplicationWindow(object):

    def __init__(self, app, root):
        self.app = app
        self.root = root
        self.config = app.config()
        self._synth_editors = {}  # Active synth editors. synth SID used as key
        
    def __setitem__(self, sid, sed):
        self._synth_editors[sid] = sed

    def __getitem__(self, sid):
        return self._synth_editors[sid]

    def keys(self):
        return self._synth_editors.keys()

    @abc.abstractmethod
    def status(self, msg):
        oscid = self.app.global_osc_id()
        print("STATUS  : /Llia/%s : %s" % (oscid, msg))

    @abc.abstractmethod
    def warning(self, msg):
        oscid = self.app.global_osc_id()
        print("WARNING : /Llia/%s : %s" % (oscid, msg))

    @abc.abstractmethod
    def start_gui_loop(self):
        return None
    
    @abc.abstractmethod
    def exit_gui(self):
        return None

    @abc.abstractmethod
    def update_progressbar(self, count, value):
        self.status("Progress %s/%s" % (value, count))
    
    @abc.abstractmethod
    def busy(self, flag, message=""):
        """
        If flag indicate application is busy.
        otherwise turn busy aspect off.
        """ 
        return None

    @abc.abstractmethod
    def tabula_rasa(self):
        pass

    @abc.abstractmethod
    def add_synth_group(self, name=""):
        return None

    @abc.abstractmethod
    def display_synth_editor(self, sid):
        pass

    @abc.abstractmethod
    def confirm_exit(self):
        return True
    
class DummyApplicationWindow(AbstractApplicationWindow):

    def __init__(self, app, *_):
        super(DummyApplicationWindow, self).__init__(app, None)
        self.group_windows=[AbstractGroupWindow(app)]

    def busy(self, flag, message=""):
        if flag:
            self.status("BUSY %s ..." % message)
        else:
            self.status("NOT BUSY")

    def add_synth_group(self, name=""):
        pass
        
        
def create_application_window(app):
    config = app.config()
    gui = str(config.gui())
    if gui.upper() == "NONE":
        if str(config["enable-splash"]).upper() != "FALSE":
            TextSplashScreen(app)
        return DummyApplicationWindow(app)
    elif gui.upper() == "TK":
        import llia.gui.tk.tk_appwindow as tkaw
        # import Tkinter as tk
        # import ttk
        # root = tk.Tk()
        appwin = tkaw.TkApplicationWindow(app)
        return appwin
    else:
        msg = "ERROR: Invalid gui: '%s'" % gui
        print(msg)
        sys.exit(1)
    
    
