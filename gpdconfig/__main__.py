#!/usr/bin/env python3

from optparse import OptionParser

import gpdconfig

parser = OptionParser(
    description = "Configures the mouse-mode controls on GPD Win devices. Replaces the official GPD WinControls app."
)

parser.add_option("-s","--set",help="Read config from FILE",metavar="FILE")
parser.add_option("-d","--dump",help="Dump config to FILE", metavar="FILE")
parser.add_option("-r","--reset",action="store_true",help="Reset to defaults")

(options,args)=parser.parse_args()

wc = gpdconfig.WinControls()

if wc.loaded and options.dump:
    with open(options.dump,"w") as wf:
        wf.write(wc.dump())

if options.reset:
    if wc.setConfig(wc.defaults):
        wc.writeConfig()

elif wc.loaded and options.set:
    with open(options.set, 'r') as rf:
        if wc.setConfig(rf.readlines()):
            wc.writeConfig()

if not options.reset and not options.dump and not options.set:
    # dump configuration to stdout
    print(wc.dump())
