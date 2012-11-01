import sublime
import sublime_plugin

class PaneHighlightCommand(sublime_plugin.EventListener):
	def get_settings(self):
		return sublime.load_settings('Preferences.sublime-settings')
	
	def on_activated(self, view):
		active_scheme = self.get_settings().get('color_scheme')
		print "active:", active_scheme
		view.settings().set('color_scheme', active_scheme)
	
	def on_deactivated(self, view):
		settings = self.get_settings()
		inactive_scheme = settings.get('color_scheme_inactive', settings.get('color_scheme'))
		print "inactive:", inactive_scheme
		view.settings().set('color_scheme', inactive_scheme)