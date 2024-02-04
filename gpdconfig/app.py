#!/usr/bin/env python3

from optparse import OptionParser

# Deal with executing either as a script or as a module
try:
    from wincontrols import WinControls, defaults
except:
    from .wincontrols import WinControls, defaults

def main():
    parser = OptionParser(
        description = "Configures the mouse-mode controls on GPD Win devices. Replaces the official GPD WinControls app."
    )

    parser.add_option("-s","--set",help="Read config from FILE",metavar="FILE")
    parser.add_option("-d","--dump",help="Dump config to FILE", metavar="FILE")
    parser.add_option("-r","--reset",action="store_true",help="Reset to defaults")
    parser.add_option("-k","--keys",action="store_true",help="List keycodes")

    (options,args)=parser.parse_args()

    if options.keys:
        from wincontrols.config import KeyCodes
        print(list(KeyCodes.code.keys()))
        return

    wc = WinControls()

    if wc.loaded and options.dump:
        with open(options.dump,"w") as wf:
            wf.write(wc.dump())

    if options.reset:
        if wc.setConfig(defaults):
            wc.writeConfig()

    elif wc.loaded and options.set:
        with open(options.set, 'r') as rf:
            if wc.setConfig(rf.readlines()):
                wc.writeConfig()

    if not options.reset and not options.dump and not options.set:
        # dump configuration to stdout
        print(wc.dump())
