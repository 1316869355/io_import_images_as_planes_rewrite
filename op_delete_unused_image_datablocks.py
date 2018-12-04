import bpy
from bpy.props import BoolProperty
from bpy.types import Operator


class IIAP_OT_delete_unused_image_datablocks(Operator):
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

def register():
    from bpy.utils import register_class
    register_class(IIAP_OT_delete_unused_image_datablocks)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(IIAP_OT_delete_unused_image_datablocks)

if __name__ == "__main__":
    register()
