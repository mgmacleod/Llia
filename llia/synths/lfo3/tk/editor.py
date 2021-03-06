# llia.synths.lfo3.tk.editor

from llia.gui.tk.tk_subeditor import TkSubEditor
import llia.gui.tk.tk_factory as factory
import llia.gui.tk.control_factory as cf
from llia.gui.tk.expslider import ExpSlider
from llia.gui.tk.tumbler import Tumbler
from llia.gui.tk.msb import MSB
from llia.synths.lfo3.lfo3_data import HARMONICS


def _msb_aspect(value, text):
    d = {'value' : value,
         'fill' : '',
         'active-fill' : '',
         'foreground' : '#c29e78',
         'active-foreground' : 'yellow',
         'outline' : '#c29e78',
         'active-outline' : 'yellow',
         'text' : text}
    return d


def create_editor(parent):
    TkLfo3Panel(parent)

class TkLfo3Panel(TkSubEditor):

    NAME = "LFO 3"
    IMAGE_FILE = "resources/LFO3/editor.png"
    TAB_FILE = "resources/Tabs/lfo.png"
    
    def __init__(self, editor):
        frame = editor.create_tab(self.NAME, self.TAB_FILE)
        frame.config(background=factory.bg())
        canvas = factory.canvas(frame,1018,663,self.IMAGE_FILE)
        canvas.pack()
        TkSubEditor.__init__(self, canvas, editor, self.NAME)
        editor.add_child_editor(self.NAME, self)

        def ratio_msb(param,x,y):
            count = len(HARMONICS)
            msb = MSB(canvas,param,editor,count)
            for i,p in enumerate(HARMONICS):
                v,text = p
                d = _msb_aspect(v,text)
                msb.define_aspect(i,v,d)
            self.add_control(param,msb)
            msb.layout((x,y))
            msb.update_aspect()
            return msb
        tumbler = Tumbler(canvas,"lfoFreq",editor, digits=5, scale=0.001)
        s_scale = cf.linear_slider(canvas, "lfoScale", editor, range_=(0,4))
        s_bias = cf.linear_slider(canvas, "lfoBias", editor, range_=(-4,4))
        s_fm = cf.linear_slider(canvas, "lfoFM", editor, range_=(0, 8))
        s_am = cf.normalized_slider(canvas, "lfoAM", editor)
        s_delay = ExpSlider(canvas, "lfoDelay", editor, range_=8)
        s_attack = ExpSlider(canvas, "lfoAttack", editor, range_=8)
        s_hold = ExpSlider(canvas, "lfoHold", editor, range_=8)
        s_release = ExpSlider(canvas, "lfoRelease", editor, range_=8)
        s_env_fm = cf.linear_slider(canvas, "lfoEnvToFreq", editor, range_=(0,8))
        s_env_bleed = cf.normalized_slider(canvas, "lfoBleed", editor)
        s_amp_a = cf.normalized_slider(canvas, "lfoAmpA", editor)
        s_amp_b = cf.normalized_slider(canvas, "lfoAmpB", editor)
        s_amp_c = cf.normalized_slider(canvas, "lfoAmpC", editor)
        self.add_control("lfoFreq", tumbler)
        self.add_control("lfoScale", s_scale)
        self.add_control("lfoBias", s_bias)
        self.add_control("lfoFM", s_fm)
        self.add_control("lfoAM", s_am)
        self.add_control("lfoDelay", s_delay)
        self.add_control("lfoAttack", s_attack)
        self.add_control("lfoHold", s_hold)
        self.add_control("lfoRelease", s_release)
        self.add_control("lfoEnvToFreq", s_env_fm)
        self.add_control("lfoBleed", s_env_bleed)
        self.add_control("lfoAmpA", s_amp_a)
        self.add_control("lfoAmpB", s_amp_b)
        self.add_control("lfoAmpC", s_amp_c)
        y0, y1 = 90, 350
        x0 = 90
        x1 = x0 + 140
        x2 = x1 + 60
        x_mod = x2 +60
        x_fm = x_mod + 75
        x_am = x_fm + 60
        x_delay = x_am + 90
        x_attack = x_delay + 60
        x_hold = x_attack + 60
        x_release = x_hold + 60
        x_env_fm = x_release + 60
        x_bleed = x_env_fm + 60
        x_a = x0
        x_b = x_a + 150
        x_c = x_b + 150
        ratio_msb("lfoModFreq", x_mod,y0)
        ratio_msb("lfoRatioA", x_a, y1)
        ratio_msb("lfoRatioB", x_b, y1)
        ratio_msb("lfoRatioC", x_c, y1)
        tumbler.layout((x0+13,y0+30))
        s_scale.widget().place(x=x1, y=y0)
        s_bias.widget().place(x=x2, y=y0)
        s_fm.widget().place(x=x_fm, y=y0)
        s_am.widget().place(x=x_am, y=y0)
        s_delay.layout(offset=(x_delay, y0),checkbutton_offset=None)
        s_attack.layout(offset=(x_attack, y0),checkbutton_offset=None)
        s_hold.layout(offset=(x_hold, y0),checkbutton_offset=None)
        s_release.layout(offset=(x_release, y0),checkbutton_offset=None)
        s_env_fm.widget().place(x=x_env_fm, y=y0)
        s_env_bleed.widget().place(x=x_bleed, y=y0)
        s_amp_a.widget().place(x=x_a+75, y=y1)
        s_amp_b.widget().place(x=x_b+75, y=y1)
        s_amp_c.widget().place(x=x_c+75, y=y1)
