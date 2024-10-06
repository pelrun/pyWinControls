# Linux version of GPD WinControls for GPD Win Mini, Win 4 and Win Max 2

A full replacement for WinControls, including features not exposed in the official app.

Shoulder buttons can be reassigned, and mouse clicks can be put anywhere. Start, Select and Menu buttons can be configured.

Delay between macro keystrokes can be changed arbitrarily, and the fixed 300ms delay after the end of the macro can be changed.

Many more keys can be assigned to buttons, not just ones you can already press.

## Usage:

```
usage: gpdconfig [-h] [-s FILE] [-d FILE] [-r] [-v] [-x] [-o] [-c] [-f FIELD] [-k] [config ...]

Configures the mouse-mode controls on GPD Win devices. Replaces the official GPD WinControls app.

positional arguments:
  config                field=value, set a button or config field to the given value.

options:
  -h, --help            show this help message and exit
  -s FILE, --set FILE   Read config from FILE
  -d FILE, --dump FILE  Dump config to FILE
  -r, --reset           Reset to defaults
  -v, --verbose         Output current config to stdout
  -x, --disable-version-check
                        Disable FW version check
  -o, --dump-raw        Dump raw config data (DEBUG)

Informational options:
  -c, --fields          List available fields
  -f FIELD, --field-help FIELD
                        Help for a specific field
  -k, --keys            List available keycodes
```

One or all settings can be changed on the command line (e.g. `gpdconfig ledmode=solid colour=FFFFFF`) or from an input file.

The following fields take keycodes (use `-k` to get a list of all valid keycodes, including mouse buttons):
`'lu', 'ld', 'll', 'lr', 'du', 'dd', 'dl', 'dr', 'a', 'b', 'x', 'y', 'l1', 'r1', 'l2', 'r2', 'l3', 'r3', 'start', 'select', 'menu', 'l41', 'l42', 'l43', 'l44', 'r41', 'r42', 'r43', 'r44'`

The following fields take numbers:
`'ldead', 'lcent', 'rdead', 'rcent', 'l4delay1', 'l4delay2', 'l4delay3', 'l4delay4', 'r4delay1', 'r4delay2', 'r4delay3', 'r4delay4'`

The following fields take other values:
`'rumble' (0,1,2) , 'ledmode' (off,solid,breathe,rotate), 'colour' (RRGGBB in hex)`

The keycodes that reference gamepad keys directly ('DPAD_','LSTICK_','RSTICK','L/R123') unfortunately only appear to work in gamepad mode, and are non-functional in mouse mode.

Have fun!
- James Churchill pelrun@gmail.com
