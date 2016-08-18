# llia.synths.lfo3.tk.editor

from llia.gui.tk.tk_subeditor import TkSubEditor
import llia.gui.tk.tk_factory as factory
import llia.gui.tk.control_factory as cf
from llia.gui.tk.expslider import ExpSlider
from llia.gui.tk.decade_control import DecadeControl
from llia.gui.tk.reciprocal_slider import ReciprocalSlider
from llia.synths.lfo3.lfo3_data import HARMONICS


def create_editor(parent):
    TkLfo3Panel(parent)

class TkLfo3Panel(TkSubEditor):

    NAME = "LFO 3"
    IMAGE_FILE = "resources/LFO3/editor.png"

    def __init__(self, editor):
        frame = editor.create_tab(self.NAME)
        frame.config(background=factory.bg())
        TkSubEditor.__init__(self, frame, editor, self.NAME)
        editor.add_child_editor(self.NAME, self)
        lab_panel = factory.image_label(frame, self.IMAGE_FILE)
        lab_panel.pack(anchor="nw", expand=False)
        dc_freq = DecadeControl(frame, "lfoFreq", editor,
                                coarse = (0.01, 10),
                                limit = (0.01, 100))
        s_scale = cf.linear_slider(frame, "lfoScale", editor, range_=(0,4))
        s_bias = cf.linear_slider(frame, "lfoBias", editor, range_=(-4,4))
        s_mod_freq = cf.discrete_slider(frame, "lfoModFreq", editor, values=HARMONICS)
        s_fm = cf.linear_slider(frame, "lfoFM", editor, range_=(0, 8))
        s_am = cf.normalized_slider(frame, "lfoAM", editor)
        s_delay = ExpSlider(frame, "lfoDelay", editor, range_=8)
        s_attack = ExpSlider(frame, "lfoAttack", editor, range_=8)
        s_hold = ExpSlider(frame, "lfoHold", editor, range_=8)
        s_release = ExpSlider(frame, "lfoRelease", editor, range_=8)
        s_env_fm = cf.linear_slider(frame, "lfoEnvToFreq", editor, range_=(0,8))
        s_env_bleed = cf.normalized_slider(frame, "lfoBleed", editor)
        s_ratio_a = cf.discrete_slider(frame, "lfoRatioA", editor, values=HARMONICS)
        s_ratio_b = cf.discrete_slider(frame, "lfoRatioB", editor, values=HARMONICS)
        s_ratio_c = cf.discrete_slider(frame, "lfoRatioC", editor, values=HARMONICS)
        s_amp_a = cf.normalized_slider(frame, "lfoAmpA", editor)
        s_amp_b = cf.normalized_slider(frame, "lfoAmpB", editor)
        s_amp_c = cf.normalized_slider(frame, "lfoAmpC", editor)
        self.add_control("lfoFreq", dc_freq)
        self.add_control("lfoScale", s_scale)
        self.add_control("lfoBias", s_bias)
        self.add_control("lfoModFreq", s_mod_freq)
        self.add_control("lfoFM", s_fm)
        self.add_control("lfoAM", s_am)
        self.add_control("lfoDelay", s_delay)
        self.add_control("lfoAttack", s_attack)
        self.add_control("lfoHold", s_hold)
        self.add_control("lfoRelease", s_release)
        self.add_control("lfoEnvToFreq", s_env_fm)
        self.add_control("lfoBleed", s_env_bleed)
        self.add_control("lfoRatioA", s_ratio_a)
        self.add_control("lfoRatioB", s_ratio_b)
        self.add_control("lfoRatioC", s_ratio_c)
        self.add_control("lfoAmpA", s_amp_a)
        self.add_control("lfoAmpB", s_amp_b)
        self.add_control("lfoAmpC", s_amp_c)
        y0, y1 = 90, 350
        x0 = 90
        x1 = x0 + 140
        x2 = x1 + 60
        x_mod = x2 + 75
        x_fm = x_mod + 60
        x_am = x_fm + 60
        x_delay = x_am + 75
        x_attack = x_delay + 60
        x_hold = x_attack + 60
        x_release = x_hold + 60
        x_env_fm = x_release + 60
        x_bleed = x_env_fm + 60
        x_a = x0
        x_b = x_a + 120
        x_c = x_b + 120
        dc_freq.layout(offset=(x0,y0), label_offset=(10,100))
        s_scale.widget().place(x=x1, y=y0)
        s_bias.widget().place(x=x2, y=y0)
        s_mod_freq.widget().place(x=x_mod, y=y0)
        s_fm.widget().place(x=x_fm, y=y0)
        s_am.widget().place(x=x_am, y=y0)
        s_delay.layout(offset=(x_delay, y0),checkbutton_offset=None)
        s_attack.layout(offset=(x_attack, y0),checkbutton_offset=None)
        s_hold.layout(offset=(x_hold, y0),checkbutton_offset=None)
        s_release.layout(offset=(x_release, y0),checkbutton_offset=None)
        s_env_fm.widget().place(x=x_env_fm, y=y0)
        s_env_bleed.widget().place(x=x_bleed, y=y0)
        s_ratio_a.widget().place(x=x_a, y=y1)
        s_ratio_b.widget().place(x=x_b, y=y1)
        s_ratio_c.widget().place(x=x_c, y=y1)
        s_amp_a.widget().place(x=x_a+60, y=y1)
        s_amp_b.widget().place(x=x_b+60, y=y1)
        s_amp_c.widget().place(x=x_c+60, y=y1)