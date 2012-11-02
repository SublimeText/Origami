import sublime
import sublime_plugin
import os
import shutil
import re

"""
This plugin creates a greyed-out version of the current color scheme,
and automatically applies it to views upon deactivation. This allows the
current pane to look highlighted, but doesn't require any futzing with
color schemes by the user. It also allows normal selection of a new
color scheme using Sublime Text 2's menu, though a new view may need to
be activated for the change to take effect.
"""

# We have to record the module path when the file is loaded because
# Sublime changes it later.
# Also Sublime gives us the wrong letter case here, but I haven't
# figured out any way to figure out what the real case is. This screws
# up commonprefix, below, and makes us nest our dim color schemes more
# deeply than perhaps would be optimal.
module_path = os.getcwdu()

settings = sublime.load_settings('Preferences.sublime-settings')

class InactivePaneCommand(sublime_plugin.EventListener):
	def __init__(self):
		settings.add_on_change('origami', lambda: self.refresh_views())
		super(InactivePaneCommand, self).__init__()

	def refresh_views(self):
		if not settings.get('fade_inactive_panes', True):
			return

		active_view_id = sublime.active_window().active_view().id()
		for window in sublime.windows():
			for v in window.views():
				if v.id() == active_view_id:
					self.on_activated(v)
				else:
					self.on_deactivated(v)

	def copy_scheme(self, scheme):
		packages_path = sublime.packages_path()
		# Unfortunately, scheme paths start with "Packages/" and
		# packages_path ends with "Packages/", so we add a .. in the middle
		# when we combine them.
		source_abs = os.path.join(packages_path, "..", scheme)

		# commonprefix isn't guaranteed to return a complete path, so we
		# take the dirname to get something real. All that really matters is
		# that the path points unambiguously to one color scheme, though
		# we'd prefer for it to be as short as possible.
		prefix = os.path.dirname(os.path.commonprefix([source_abs, module_path]))
		source_rel = os.path.relpath(source_abs, prefix)

		# Reconstruct the relative path inside of our module directory--we
		# have something of a shadow copy of the scheme.
		destination = os.path.join(module_path, source_rel)
		if (os.path.isfile(destination)):
			return destination, True

		destdir = os.path.dirname(destination)
		if not os.path.isdir(destdir):
			os.makedirs(destdir)
		shutil.copy(source_abs, destination)

		return destination, False

	def dim_scheme(self, scheme):
		def dim_hex(hex_val):
			grey_scale = .2
			orig_scale = 1-grey_scale
			return int(int(hex_val,16)*orig_scale+127*grey_scale)
		def dim_rgb(rgb_match):
			hex_str = rgb_match.group()
			r,g,b = hex_str[1:3],hex_str[3:5],hex_str[5:7]
			#average toward grey
			r = dim_hex(r)
			g = dim_hex(g)
			b = dim_hex(b)
			return "#{0:02x}{1:02x}{2:02x}".format(r,g,b)

		f = open(scheme)
		text = f.read()
		f.close()

		text = re.sub("#[0-9a-fA-F]{6}", dim_rgb, text)
		f = open(scheme, 'w')
		f.write(text)
		f.close()

	def on_activated(self, view):
		active_scheme = settings.get('color_scheme')
		view.settings().set('color_scheme', active_scheme)

	def on_deactivated(self, view):
		if not settings.get('fade_inactive_panes', True):
			return

		active_scheme = settings.get('color_scheme')

		inactive_scheme, existed_already = self.copy_scheme(active_scheme)
		if not existed_already:
			self.dim_scheme(inactive_scheme)

		# Sublime Text 2 only likes relative paths for its color schemes
		prefix = os.path.dirname(os.path.commonprefix([inactive_scheme, module_path]))
		inactive_scheme_rel = os.path.relpath(inactive_scheme, prefix)
		inactive_scheme_rel = os.path.join("Packages", inactive_scheme_rel).replace("\\", "/")
		view.settings().set('color_scheme', inactive_scheme_rel)
