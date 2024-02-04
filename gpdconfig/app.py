#!/usr/bin/env python3

import sys
import argparse

sys.tracebacklimit = 0

# Deal with executing either as a script or as a module
try:
    from wincontrols import WinControls, defaults
    from wincontrols.config import KeyCodes
except:
    from .wincontrols import WinControls, defaults
    from .wincontrols.config import KeyCodes

def main():
    parser = argparse.ArgumentParser(
        description = "Configures the mouse-mode controls on GPD Win devices. Replaces the official GPD WinControls app.",
    )

    parser.add_argument("-s","--set", metavar="FILE", help="Read config from FILE",)
    parser.add_argument("-d","--dump", metavar="FILE", help="Dump config to FILE")
    parser.add_argument("-r","--reset", action="store_true", help="Reset to defaults")
    parser.add_argument("-v","--verbose", action="store_true", help="Output current config to stdout")

    group = parser.add_argument_group("Informational options")
    group.add_argument("-c","--fields", action="store_true", help="List available fields")
    group.add_argument("-f","--field-help", metavar="FIELD", help="Help for a specific field")
    group.add_argument("-k","--keys", action="store_true", help="List available keycodes")

    parser.add_argument('config', nargs='*', help='field=value, set a button or config field to the given value.')

    options=parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        return

    if options.field_help:
        if options.field_help not in WinControls().field:
            print(f"Unknown field '{options.field_help}'")
            return
        print(options.field_help, ':', WinControls().field[options.field_help].help())
        return

    #TODO: group types of field together and print them in a more readable way
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
    if options.config:
        if wc.setConfig(options.config):
            wc.writeConfig()

    if options.verbose:
        # dump configuration to stdout
        print(wc.dump())
