# llia.synths.xover.xover_proxy
# 2016.07.03

from __future__ import print_function

from llia.gui.pallet import default_pallet, Pallet
from llia.synth_proxy import SynthSpecs, SynthProxy
from llia.synths.xover.xover_data import program_bank
# from llia.synths.orgn.orgn_pp import pp_orgn
# from llia.synths.orgn.orgn_gen import gen_orgn_program

specs = SynthSpecs("XOver");

class XOverProxy(SynthProxy):

    def __init__(self, app, id_):
        super(XOverProxy, self).__init__(app, specs, id_, program_bank)
        self._editor = None

    def create_subeditors(self):
        pass

xover_pallet = Pallet(default_pallet)

specs["constructor"] = XOverProxy
specs["description"] = "Crossover Filter Effect"
specs["audio-output-buses"] = (("outbus", 1),)
specs["audio-input-buses"] = (("inbus", 1),)
# specs["program-generator"] = gen_stepfilter_program
specs["is-efx"] = True
# specs["pretty-printer"] = pp_stepfilter
specs["help"] = "xover"
