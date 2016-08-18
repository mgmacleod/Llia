# vllia.synths.pulsegen.pulsegen_proxy

from __future__ import print_function

from llia.gui.pallet import default_pallet, Pallet
from llia.synth_proxy import SynthSpecs, SynthProxy
from llia.synths.pulsegen.pulsegen_data import program_bank, pp, random_pulsegen

specs = SynthSpecs("PulseGen")

class PulsegenProxy(SynthProxy):

    def __init__(self, app, id_):
        super(PulsegenProxy, self).__init__(app, specs, id_, program_bank)
        self.app = app
        
    def create_subeditors(self):
        pass
        gui = self.app.config["gui"].upper()
        if gui == "TK":
            from llia.synths.pulsegen.tk.editor import create_editor
            appwin = self.app.main_window()
            parent_editor = appwin[self.sid]
            create_editor(parent_editor)
            

pulsegen_pallet = Pallet(default_pallet)
pulsegen_pallet["SLIDER-TROUGH"] = "#432703"
pulsegen_pallet["SLIDER-OUTLINE"] = "#42033E"

specs["constructor"] = PulsegenProxy
specs["description"] = "Complex Pulse generator"
specs["keymodes"] = ("EFX", )
specs["audio-output-buses"] = []
specs["audio-input-buses"] = []
specs["control-output-buses"] = ("outbusY", "outbusZ")
specs["pretty-printer"] = pp
specs["program-generator"] = random_pulsegen
specs["is-efx"] = True
specs["help"] = "PULSEGEN"
specs["pallet"] = pulsegen_pallet