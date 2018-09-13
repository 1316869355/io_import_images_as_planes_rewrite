from math import (
    ceil,
)
import bpy
from bpy.types import (
    Operator
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


def arange_objects(self, context, obs):
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


class IIAP_OP_arange_objects(Operator):
    """Arange Objects in Grid"""
    bl_idname = 'io.arange_objects'
    bl_label = 'Grid Arange'
    bl_description = 'Arange Objects in Grid'
    bl_options = {'REGISTER', 'UNDO'}

    row_count: IntProperty(
        name='Rows',
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
        return obs

    def execute(self, context):
        '''imageplane from selected texture node'''
        obs = context.selected_objects
        arange_objects(self, context, obs)
        return {'FINISHED'}
