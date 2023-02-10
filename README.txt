=== what is vvvert1g0 ===

vvvert1g0, by Benjamin Newman, is a command-line terminal demake[1]
of the puzzle-platform game VVVVVV, by Terry Cavanagh.[2]

It is designed to be played in a VT100-compatible character-cell terminal,
such as the Mac OS or Linux terminals -- the characters 'v', 't', '1', and '0'
in the title are a reference to the VT100,[3] one of the first hardware
console terminals to feature this kind of character-cell graphics.

[1] https://tvtropes.org/pmwiki/pmwiki.php/Main/VideoGameDemake
[2] https://thelettervsixtim.es
[3] https://en.wikipedia.org/wiki/VT100

=== how to run ===

vvvert1g0 is implemented as a Python script, vvvert1g0.py, using the curses
library for terminal graphics control.  It should run on any console supported
by that library.  It runs in color on terminals that support it (recommended).

vvvert1g0.py is compatible with later versions of Python 2 and with Python 3,
and has been tested on both Python 2.7 and Python 3.10.

In keeping with the dimesions of the historical VT100 terminal,
vvvert1g0 expects a terminal size of 80x24 (80 columns by 24 rows).

To run vvvert1g0:

> python vvvert1g0.py mapfile.vvv

Included map files:

- tutorial.vvv:
    a series of short and not-at-all-challenging levels
    introducing the game's features and mechanics one at a time

- demo.vvv:
    a single level, moderately challenging,
    demonstrating most of the game's mechanics

More map files will be added in future updates.

=== how to play ===

The best introduction to the game's icons, controls, and mechanics
is to play the tutorial map file, tutorial.vvv

Use the arrow keys to move left and right.  You need only tap the key,
and will continue moving in the same direction until another key is pressed.

Use the up and down arrow keys to reverse the direction of gravity
when standing on a solid surface.

Get your character, represented as an 'A' when right-side-up
and as a 'V' when upside-down, to the exit, represented as 'E'.

=== how to create levels ===

Although I've used the extension .vvv for the included map files,
vvvert1g0 maps are plain ASCII text files and can be created and edited
in any text editor.

Levels should fit within an 80x24 terminal window, and are separated in the
map file by a line that consists of two hyphens (--) on a line by themselves.

--- characters that represent gameplay elements ---

'A' -- the starting space for the player character (right-side-up)
'V' -- the starting space for the player character (upside-down)

' ' -- empty space
'[]' -- solid walls
'X' -- spikes (deadly)

'=' -- bouncy floor (will automatically reverse gravity on contact)
'||' -- bounce field (will reverse gravity when the player passes through it*)

* bounce field cells must be used in pairs because the gravity flip occurs
  when passing between two such cells

's' -- a save point (the currently active save point will be rendered as 'S')
'E' -- the exit of the level (can be more than one)

'$' -- a coin
'1234567890' -- a gate which will open when N coins are collected (0 for ten)

'abc' -- portals: see below for detailed instructions on how to set up portals

'D' -- start of the status display (showing coins, elapsed time, and deaths)*

* it's not required to include the status display in every level
* allow 24-28 characters of space for the status display

--- quoting ---

Use double-quotes (") to escape text that should be displayed as-is without
activating any game logic.  If a quoted section  extends to the end of a line
it doesn't have to be closed.  The double-quote itself will be replaced by a
blank space so that the alignment of characters in the input file is preserved.

Within quotes, color is suppressed by default.  Use the following characters to
toggle color back on, for example as used in the tutorial to display gameplay
elements within the tutorial text:

_ (underscore) -- toggles color within quotes, is rendered as a blank space
` (backtick) -- toggles color within quotes, is rendered as ' (single quote)
{} (braces) -- toggles color within quotes, is rendered as () (parentheses)

Levels with quotes should be designed so that the player character cannot
reach or interact with the quoted text.

--- portals ---

The characters 'abc' represent portals.  Each distinct character is a
different color of portal, and there can be up to two portals of each color.
Each portal can be larger than one cell, but should have a rectangular frame.
If there are two portals of a color, they should be the same size and shape.

If there are two portals of a color, they are linked to each other.  A player
entering one of the portals will emerge from the linked portal on the opposite
side.  If there is one portal of a color, a player entering it will emerge on
the opposite side of the same portal.  This can be used to create crossings.

--- validation ---

Logic to validate map files will be added in a future update.

=== LICENSE ===

This work is licensed under the Creative Commons
Attribution-ShareAlike 4.0 International License.

To view a copy of this license,
visit http://creativecommons.org/licenses/by-sa/4.0/
or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
