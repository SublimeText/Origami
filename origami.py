import sublime, sublime_plugin

XMIN, YMIN, XMAX, YMAX = list(range(4))

def increment_if_greater_or_equal(x, threshold):
	if x >= threshold:
		return x+1
	return x

def decrement_if_greater(x, threshold):
	if x > threshold:
		return x-1
	return x

def pull_up_cells_after(cells, threshold):
		return [	[x0,decrement_if_greater(y0, threshold),
		        	x1,decrement_if_greater(y1, threshold)] for (x0,y0,x1,y1) in cells]

def push_right_cells_after(cells, threshold):
		return [	[increment_if_greater_or_equal(x0, threshold),y0,
		        	increment_if_greater_or_equal(x1, threshold),y1] for (x0,y0,x1,y1) in cells]

def push_down_cells_after(cells, threshold):
		return [	[x0,increment_if_greater_or_equal(y0, threshold),
		        	x1,increment_if_greater_or_equal(y1, threshold)] for (x0,y0,x1,y1) in cells]

def pull_left_cells_after(cells, threshold):
		return [	[decrement_if_greater(x0, threshold),y0,
		        	decrement_if_greater(x1, threshold),y1] for (x0,y0,x1,y1) in cells]

def cells_adjacent_to_cell_in_direction(cells, cell, direction):
	fn = None
	if direction == "up":
		fn = lambda orig, check: orig[YMIN] == check[YMAX]
	elif direction == "right":
		fn = lambda orig, check: orig[XMAX] == check[XMIN]
	elif direction == "down":
		fn = lambda orig, check: orig[YMAX] == check[YMIN]
	elif direction == "left":
		fn = lambda orig, check: orig[XMIN] == check[XMAX]
	
	if fn:
		return [c for c in cells if fn(cell, c)]
	return None

class PaneCommand(sublime_plugin.WindowCommand):
	"Abstract base class for commands."
	
	def get_layout(self):
		layout = self.window.get_layout()
		print(layout)
		cells = layout["cells"]
		rows = layout["rows"]
		cols = layout["cols"]	
		return rows, cols, cells
	
	def get_cells(self):
		return self.get_layout()[2]
	
	def adjacent_cells(self, direction):
		cells = self.get_cells()
		current_group = self.window.active_group()
		return cells_adjacent_to_cell_in_direction(cells, cells[current_group], direction)
	
	def duplicated_views(self, original_group, duplicating_group):
		original_views = self.window.views_in_group(original_group)
		original_buffers = [v.buffer_id() for v in original_views]
		potential_dupe_views = self.window.views_in_group(duplicating_group)
		dupe_views = []
		for pd in potential_dupe_views:
			if pd.buffer_id() in original_buffers:
				dupe_views.append(pd)
		return dupe_views
	
	def travel_to_pane(self, direction):
		adjacent_cells = self.adjacent_cells(direction)
		if len(adjacent_cells) > 0:
			cells = self.get_cells()
			new_group_index = cells.index(adjacent_cells[0])
			self.window.focus_group(new_group_index)
	
	def carry_file_to_pane(self, direction):
		view = self.window.active_view()
		if not view:
			# If we're in an empty group, there's no active view
			return
		window = self.window
		group = self.travel_to_pane(direction)
		window.set_view_index(view, window.active_group(), 0)
	
	def clone_file_to_pane(self, direction):
		window = self.window
		view = window.active_view()
		if not view:
			# If we're in an empty group, there's no active view
			return
		group, original_index = window.get_view_index(view)
		window.run_command("clone_file")
		
		# If we move the cloned file's tab to the left of the original's,
		# then when we remove it from the group, focus will fall to the
		# original view.
		new_view = window.active_view()
		window.set_view_index(new_view, group, original_index)
		self.carry_file_to_pane(direction)
	
	def create_pane_with_file(self,direction):
		self.create_pane(direction)
		self.carry_file_to_pane(direction)

	def create_pane(self, direction):
		window = self.window
		rows, cols, cells = self.get_layout()
		current_group = window.active_group()
		
		old_cell = cells.pop(current_group)
		new_cell = []
		
		if direction in ("up", "down"):
			cells = push_down_cells_after(cells, old_cell[YMAX])
			rows.insert(old_cell[YMAX], (rows[old_cell[YMIN]] + rows[old_cell[YMAX]]) / 2)
			new_cell = [old_cell[XMIN], old_cell[YMAX], old_cell[XMAX], old_cell[YMAX]+1]
			old_cell = [old_cell[XMIN], old_cell[YMIN], old_cell[XMAX], old_cell[YMAX]]
		
		elif direction in ("right", "left"):
			cells = push_right_cells_after(cells, old_cell[XMAX])
			cols.insert(old_cell[XMAX], (cols[old_cell[XMIN]] + cols[old_cell[XMAX]]) / 2)
			new_cell = [old_cell[XMAX], old_cell[YMIN], old_cell[XMAX]+1, old_cell[YMAX]]
			old_cell = [old_cell[XMIN], old_cell[YMIN], old_cell[XMAX], old_cell[YMAX]]
		
		if new_cell:
			if direction in ("left", "up"):
				focused_cell = new_cell
				unfocused_cell = old_cell
			else:
				focused_cell = old_cell
				unfocused_cell = new_cell
			cells.insert(current_group, focused_cell)
			cells.append(unfocused_cell)
			layout = {"cols": cols, "rows": rows, "cells": cells}
			print(layout)
			window.set_layout(layout)
	
	def destroy_pane(self, direction):
		window = self.window
		rows, cols, cells = self.get_layout()
		current_group = window.active_group()
		
		cell_to_remove = None
		current_cell = cells[current_group]
		
		adjacent_cells = cells_adjacent_to_cell_in_direction(cells, current_cell, direction)
		print("number adjacent: ", len(adjacent_cells))
		if len(adjacent_cells) == 1:
			cell_to_remove = adjacent_cells[0]
		
		if cell_to_remove:
			active_view = window.active_view()
			group_to_remove = cells.index(cell_to_remove)
			dupe_views = self.duplicated_views(current_group, group_to_remove)
			for d in dupe_views:
				window.focus_view(d)
				window.run_command('close')
			if active_view:
				window.focus_view(active_view)
			
			cells.remove(cell_to_remove)
			if direction == "up":
				rows.pop(cell_to_remove[YMAX])
				adjacent_cells = cells_adjacent_to_cell_in_direction(cells, cell_to_remove, "down")
				for cell in adjacent_cells:
					cells[cells.index(cell)][YMIN] = cell_to_remove[YMIN]
				cells = pull_up_cells_after(cells, cell_to_remove[YMAX])
			elif direction == "right":
				cols.pop(cell_to_remove[XMIN])
				adjacent_cells = cells_adjacent_to_cell_in_direction(cells, cell_to_remove, "left")
				for cell in adjacent_cells:
					cells[cells.index(cell)][XMAX] = cell_to_remove[XMAX]
				cells = pull_left_cells_after(cells, cell_to_remove[XMIN])
			elif direction == "down":
				rows.pop(cell_to_remove[YMIN])
				adjacent_cells = cells_adjacent_to_cell_in_direction(cells, cell_to_remove, "up")
				for cell in adjacent_cells:
					cells[cells.index(cell)][YMAX] = cell_to_remove[YMAX]
				cells = pull_up_cells_after(cells, cell_to_remove[YMIN])
			elif direction == "left":
				cols.pop(cell_to_remove[XMAX])
				adjacent_cells = cells_adjacent_to_cell_in_direction(cells, cell_to_remove, "right")
				for cell in adjacent_cells:
					cells[cells.index(cell)][XMIN] = cell_to_remove[XMIN]
				cells = pull_left_cells_after(cells, cell_to_remove[XMAX])
			
			layout = {"cols": cols, "rows": rows, "cells": cells}
			print(layout)
			window.set_layout(layout)


class TravelToPaneCommand(PaneCommand):
	def run(self, direction):
		self.travel_to_pane(direction)


class CarryFileToPaneCommand(PaneCommand):
	def run(self, direction):
		self.carry_file_to_pane(direction)


class CloneFileToPaneCommand(PaneCommand):
	def run(self, direction):
		self.clone_file_to_pane(direction)


class CreatePaneWithFileCommand(PaneCommand):
	def run(self, direction):
		self.create_pane_with_file(direction)


class CreatePaneCommand(PaneCommand):
	def run(self, direction):
		print("creating")
		self.create_pane(direction)


class DestroyPaneCommand(PaneCommand):
	def run(self, direction):
		self.destroy_pane(direction)
