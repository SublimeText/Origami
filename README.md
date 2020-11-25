Origami
======
Origami is a new way of thinking about panes in Sublime Text 2 and 3: you tell Sublime Text where you want a new pane, and it makes one for you. It works seamlessly alongside the built-in layout commands.

Ordinarily one uses the commands under View>Layout, or if one is quite intrepid a custom keyboard shortcut can be made to give a specific layout, but both of these solutions were unsatisfactory to me. Perhaps they were to you too! That's what this plugin is for.

Try it out! I think you'll like it.

Keyboard shortcuts
------------------
Origami is driven by keyboard shortcuts. By default, these keyboard shortcuts are all two-stage, and are hidden behind `command+k`. First press `command+k`, then press the arrow keys with modifiers:

* no modifiers: travel to an adjacent pane
* `shift`: carry the current file to the destination
* `alt` (`option`): clone the current file to the destination
* `command`: create an adjacent pane
* `command+shift`: destroy an adjacent pane

These keyboard shortcuts are designed to make it really easy to modify the layout of your editor.

Additionally, Origami allows one to zoom the current pane, making it take up a large portion of the window. As above, first press `command+k`, then press:

* `command+z`: Zoom the current pane so it takes up 90% of the screen (the fraction is changeable in the keybindings)
* `shift+command+z`: Unzoom: equally space all panes

It is also possible to edit the pane sizes. After `command+k` press:
* `command+r`: Adjust the top and bottom separator
* `command+c`: Adjust the left and right separator

In the keybindings you can change a `mode` which specifies which separation lines you want to edit.
* `ALL` means all horizontal (or vertical) separators
* `RELEVANT` means all horizontal (or vertical) separators which intersect the column (row) of the selected row.
* `NEAREST` means top and bottom (or left and right) separators. This is the default `mode`.
* `BEFORE` means top (or left) separator
* `AFTER` means bottom (or right) separator

(Note: Windows and Linux use `ctrl` instead of `command`.)

Automation
----------
You can have Origami automatically zoom the active pane by setting `auto_zoom_on_focus` in your Origami user preferences. Set it to `true` for the default zoom, or set it to a user-definable fraction of the screen, such as `0.75`.

Origami can also automatically close a pane for you once you've closed the last file in it. Just set `auto_close_empty_panes` to true in the Origami preferences.

Install
-------

Search for Origami on [Package Control](https://sublime.wbond.net/)!
