#!/usr/bin/env python3

from optparse import OptionParser, OptionGroup

# Deal with executing either as a script or as a module
try:
    from wincontrols import WinControls, defaults
    from wincontrols.config import KeyCodes
except:
    from .wincontrols import WinControls, defaults
    from .wincontrols.config import KeyCodes

def main():
    parser = OptionParser(
        usage = "usage: %prog [options] [field=value,...]",
        description = "Configures the mouse-mode controls on GPD Win devices. Replaces the official GPD WinControls app."
    )

    parser.add_option("-s","--set",help="Read config from FILE",metavar="FILE")
    parser.add_option("-d","--dump",help="Dump config to FILE", metavar="FILE")
    parser.add_option("-r","--reset",action="store_true",help="Reset to defaults")
    parser.add_option("-v","--verbose",action="store_true",help="Output current config to stdout")

    group = OptionGroup(parser, "Extra help")
    group.add_option("-f","--fields",action="store_true",help="List available fields")
    group.add_option("-k","--keys",action="store_true",help="List available keycodes")

    parser.add_option_group(group)

    (options,args)=parser.parse_args()

    if options.fields:
        print("Available config fields:\n",list(WinControls().field.keys()))

    if options.keys:
        print("Available keycodes:\n",list(KeyCodes.code.keys()))

    if options.fields or options.keys:
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

    # parse any additional arguments as configuration lines
    if args:
        if wc.setConfig(args):
            wc.writeConfig()

    if options.verbose:
        # dump configuration to stdout
        print(wc.dump())
