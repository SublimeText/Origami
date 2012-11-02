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


def reset():
	"""Delete temporaryly generated dimmed files."""
	for root, dirs, files in os.walk(module_path):
		if '.git' in dirs:
			dirs.remove('.git')  # do not iterate over .git or subdirs
		for di in dirs:
			shutil.rmtree(os.path.join(root, di))


reset()


class Origami(object):
	enabled    = settings.get('fade_inactive_panes', False)
	grey_scale = settings.get('fade_inactive_panes_grey_scale')

	def __init__(self):
		# Register some callbacks
		def on_settings_change():
			if settings.get('fade_inactive_panes') != self.enabled \
					or settings.get('fade_inactive_panes_grey_scale') != self.grey_scale:

				print("settings changed")
				# Calling reset() here mostly results in the newly generated files also being deleted,
				# it should be enough to delete old files when ST starts.
				# reset()
				self.refresh_views()

				self.enabled    = settings.get('fade_inactive_panes')
				self.grey_scale = settings.get('fade_inactive_panes_grey_scale')


			print("settings did not change")

		def add_on_change(setting, callback):
			settings.clear_on_change(setting)
			settings.add_on_change(setting, callback)

		add_on_change('origami',                        lambda: self.refresh_views())
		add_on_change('fade_inactive_panes_grey_scale', on_settings_change)
		add_on_change('fade_inactive_panes',            on_settings_change)

		super(Origami, self).__init__()

	def refresh_views(self, disable=False):
		disable = disable or (self.enabled and self.enabled != settings.get('fade_inactive_panes'))
		active_view_id = sublime.active_window().active_view().id()
		for window in sublime.windows():
			for v in window.views():
				if v.settings().get('is_widget'):
					continue
				if disable or v.id() == active_view_id:
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
		print("[Origami] Generating dimmed color scheme for '%s'" % scheme)

		def dim_hex(hex_val):
			grey_scale = settings.get('fade_inactive_panes_grey_scale', .2)
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
		if view is None or view.settings().get('is_widget'):
			return
		default_scheme = view.settings().get('default_scheme', settings.get('color_scheme'))
		if default_scheme:
			view.settings().set('color_scheme', default_scheme)
			view.settings().erase('default_scheme')
		elif self.enabled:
			view.settings().erase('color_scheme')

	def on_deactivated(self, view):
		if view is None or view.settings().get('is_widget'):
			return

		if not settings.get('fade_inactive_panes', True):
			return

		# Reset to the base color scheme first if there was any
		self.on_activated(view)

		active_scheme = view.settings().get('color_scheme')
		view.settings().erase('color_scheme')
		default_scheme = view.settings().get('color_scheme')
		if active_scheme != default_scheme:
			# Because the settings do not equal after removing the view-depended component
			# the view's color scheme is expicitly set so save it for later.
			view.settings().set('default_scheme', active_scheme)

		inactive_scheme, existed_already = self.copy_scheme(active_scheme)
		if not existed_already:
			self.dim_scheme(inactive_scheme)

		# Sublime Text 2 only likes relative paths for its color schemes
		prefix = os.path.dirname(os.path.commonprefix([inactive_scheme, module_path]))
		inactive_scheme_rel = os.path.relpath(inactive_scheme, prefix)
		inactive_scheme_rel = os.path.join("Packages", inactive_scheme_rel).replace("\\", "/")
		view.settings().set('color_scheme', inactive_scheme_rel)


origami = Origami()


class InactivePaneCommand(sublime_plugin.EventListener):
	delay = 150
	
	def on_activated(self, view):
		if view is None or view.settings().get('is_widget'):
			return
		sublime.set_timeout(lambda: origami.on_activated(view), self.delay)

	def on_deactivated(self, view):
		if view is None or view.settings().get('is_widget'):
			return
		sublime.set_timeout(lambda: origami.on_deactivated(view), self.delay)
