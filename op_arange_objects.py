from math import (
	ceil,
)
import bpy
from bpy.types import (
	Operator,
	GizmoGroup,
)
from bpy.props import (
	IntProperty,
	FloatProperty,
)
from mathutils import (
	Vector,
	Matrix,
)


def calc_row_count(self, obs):
	if self.row_count == 1:
		return len(obs)
	return ceil(len(obs) / self.row_count)


def grid_arange(self, context, obs):
	obs_per_row = calc_row_count(self, obs)

	current_row = 0
	current_col = 0
	for i, ob in enumerate(obs):
		ob.location = Vector((current_col * self.offset_x,
							  current_row * self.offset_y * -1,
							  0)) + context.scene.cursor_location
		current_col += 1
		if current_col == obs_per_row:
			current_col = 0
			current_row += 1


class OBJECT_OT_grid_arange(Operator):
	"""Arange Objects in Grid"""
	bl_idname = 'object.grid_arange'
	bl_label = 'Grid Arange'
	bl_description = 'Arange Objects in Grid'
	bl_options = {'REGISTER', 'UNDO'}

	row_count: IntProperty(
		name='Max. Rows',
		default=1,
		min=1,
		soft_min=1,
	)
	offset_x: FloatProperty(
		name='Offset X',
		default=2
	)
	offset_y: FloatProperty(
		name='Offset Y',
		default=2
	)

	@classmethod
	def poll(cls, context):
		'''If texture node with image is active'''
		obs = context.selected_objects
		return (obs and context.mode == 'OBJECT')

	def execute(self, context):
		'''imageplane from selected texture node'''
		obs = context.selected_objects
		grid_arange(self, context, obs)
		return {'FINISHED'}

	def invoke(self, context, event):
		self.execute(context)
		if context.space_data.type == 'VIEW_3D':
			wm = context.window_manager
			wm.gizmo_group_type_add(OBJECT_GGT_grid_arange_gizmogroup.bl_idname)
			print('ADDED GIZMO')
		return {'FINISHED'}


class OBJECT_GGT_grid_arange_gizmogroup(GizmoGroup):
	bl_idname = "OBJECT_GGT_grid_arange_gizmogroup"
	bl_label = "Grid Arange Gizmo"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'WINDOW'
	bl_options = {'3D'}

	# Helper functions
	@staticmethod
	def my_target_operator(context):
		wm = context.window_manager
		op = wm.operators[-1] if wm.operators else None
		if op.bl_idname == 'OBJECT_OT_grid_arange':
			return op
		return None

	@classmethod
	def poll(cls, context):
		op = cls.my_target_operator(context)
		if op is None:
			wm = context.window_manager
			wm.gizmo_group_type_remove(OBJECT_GGT_grid_arange_gizmogroup.bl_idname)
			print('removed gizmo')
			return False
		return True

	def widget_row_count_matrix(self, context, op):
		mat = Matrix.Rotation(1.5, 4, 'X')
		mat.translation = context.scene.cursor_location
		mat.translation.x += op.offset_x * -1
		return mat

	def setup(self, context):
		print('SETUP GIZMO')
		op = OBJECT_GGT_grid_arange_gizmogroup.my_target_operator(context)

		def rows_get_cb():
			# op = OBJECT_GGT_grid_arange_gizmogroup.my_target_operator(context)
			return op.row_count

		def rows_set_cb(value):
			# op = OBJECT_GGT_grid_arange_gizmogroup.my_target_operator(context)
			op.row_count = int(value)
			op.execute(context)

		mpr = self.gizmos.new("GIZMO_GT_arrow_3d")
		mpr.target_set_handler("offset", get=rows_get_cb, set=rows_set_cb)
		mpr.draw_style = 'BOX'
		mpr.color = 0.9, 0.0, 0.0
		mpr.alpha = 0.9
		mpr.scale_basis = 1.0
		mpr.matrix_basis = self.widget_row_count_matrix(context, op)

		self.widget_row_count = mpr

	def refresh(self, context):
		op = OBJECT_GGT_grid_arange_gizmogroup.my_target_operator(context)
		print('REFRESHING GIZMO')
		mpr = self.widget_row_count
		mpr.matrix_basis = self.widget_row_count_matrix(context, op)
