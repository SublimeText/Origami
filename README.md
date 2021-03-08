Origami
=======

Origami is a new way of thinking about panes in Sublime Text: you tell Sublime Text where you want a new pane, and it makes one for you. It works seamlessly alongside the built-in layout commands.

Ordinarily one uses the commands under View>Layout, or if one is quite intrepid a custom keyboard shortcut can be made to give a specific layout, but both of these solutions were unsatisfactory to me. Perhaps they were to you too! That's what this plugin is for.

Try it out! I think you'll like it.

Keyboard shortcuts
------------------

> **NOTE**: Windows and Linux use `ctrl` instead of `command`.

Origami is driven by keyboard shortcuts. By default, these keyboard shortcuts are all two-stage, and are hidden behind `command+k`. First press `command+k`, then press the arrow keys with modifiers:

| First       | Then                    | Action                                    |
| ----------- | ----------------------- | ----------------------------------------- |
| `command+k` | ▲►▼◄                  | travel to an adjacent pane                |
| `command+k` | `shift`+▲►▼◄          | carry the current file to the destination |
| `command+k` | `alt` (`option`)+▲►▼◄ | clone the current file to the destination |
| `command+k` | `command`+▲►▼◄        | create an adjacent pane                   |
| `command+k` | `command+shift`+▲►▼◄  | destroy an adjacent pane                  |

These keyboard shortcuts are designed to make it really easy to modify the layout of your editor.

> **NOTE**: The following keyboard shortcuts for zooming and editing pane sizes are not enabled by default due to a conflict with built-in ST features. Open the `Preferences: Origami Key Bindings` from the Command Palette to enable or edit them, or just use the Command Palette to trigger those commands.


Additionally, Origami allows one to zoom the current pane, making it take up a large portion of the window:

| First       | Then              | Action                           |
| ----------- | ----------------- | -------------------------------- |
| `command+k` | `command+z`       | Zoom the current pane so it takes up 90% of the screen (the fraction is changeable in the keybindings) |
| `command+k` | `shift+command+z` | Un-zoom: equally space all panes |

It is also possible to edit the pane sizes:

| First       | Then        | Action                              |
| ----------- | ------------| ----------------------------------- |
| `command+k` | `command+r` | Adjust the top and bottom separator |
| `command+k` | `command+c` | Adjust the left and right separator |

In the keybindings you can change a `mode` which specifies which separation lines you want to edit.
* `ALL` means all horizontal (or vertical) separators
* `RELEVANT` means all horizontal (or vertical) separators which intersect the column (row) of the selected row.
* `NEAREST` means top and bottom (or left and right) separators. This is the default `mode`.
* `BEFORE` means top (or left) separator
* `AFTER` means bottom (or right) separator

Automation
----------

You can have Origami automatically zoom the active pane by setting `auto_zoom_on_focus` in your Origami user preferences. Set it to `true` for the default zoom, or set it to a user-definable fraction of the screen, such as `0.75`.

Origami can also automatically close a pane for you once you've closed the last file in it. Just set `auto_close_empty_panes` to true in the Origami preferences.

Installation
------------

#### Using package control

1. Open up the command palette: <kbd>ctrl+shift+p</kbd> (Linux, Windows) / <kbd>cmd+shift+p</kbd> (macOS)
2. Search for `Package Control: Install Package`
3. Search for `Origami`
4. Hit <kbd>enter</kbd> :wink:

#### Using the command line

If you want to contribute to this package, first thanks, and second, you should download this using `git` so that you can propose your changes.

```bash
cd "%APPDATA%\Sublime Text 3\Packages"             # on Windows
cd ~/Library/Application\ Support/Sublime\ Text\ 3 # on Mac
cd ~/.config/sublime-text-3                        # on Linux

git clone "https://github.com/SublimeText/Origami.git"
```
