import bpy
from bpy.types import (
    Operator,
)
from bpy.props import (
    BoolProperty
)


class IIAP_OP_delete_unused_image_datablocks(Operator):
    """docstring for IMAGE_OT_delete_unused_image_datablocks."""
    bl_idname = 'image.delete_unused_image_datablocks'
    bl_label = 'Delete unused image(datablocks)'
    bl_description = 'Delete unused image datablocks (or all with shift pressed)'
    bl_options = {'REGISTER', 'UNDO'}

    all: BoolProperty(
        name='Delete all image datablocks',
        default=False
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for image in bpy.data.images:
            if image.users == 0 or self.all:
                bpy.data.images.remove(image)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.all = event.shift
        self.execute(context)
        return {'FINISHED'}
