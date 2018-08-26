import bpy
from bpy.types import (
    Operator,
)
from bpy.props import (
    BoolProperty
)


class MATERIAL_OT_delete_unused_image_datablocks(Operator):
    """docstring for IMAGE_OT_delete_unused_image_datablocks."""
    bl_idname = 'material.delete_unused_material_datablocks'
    bl_label = 'Delete unused material(datablocks)'
    bl_description = 'Delete unused material datablocks (or all with shift pressed)'
    bl_options = {'REGISTER', 'UNDO'}

    all: BoolProperty(
        name='Delete all material datablocks',
        default=False
    )

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):
        for material in bpy.data.materials:
            if material.users == 0 or self.all:
                bpy.data.materials.remove(material)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.all = event.shift
        self.execute(context)
        return {'FINISHED'}
