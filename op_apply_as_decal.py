import bpy
from bpy.types import (
    Operator
)


def apply_as_decal(self, context):
    decal = context.active_object
    target = [ob for ob in context.selected_objects if not ob is decal][0]
    print('Decal: ', decal.name, 'Target: ', target.name)

    # Add subsurf
    subs = decal.modifiers.new(name='Subsurf', type='SUBSURF')
    subs.subdivision_type = 'SIMPLE'
    subs.levels = 2

    # Add shrinkwrap modifier
    shrink = decal.modifiers.new(name='Shrinkwrap', type='SHRINKWRAP')
    shrink.target = target
    shrink.offset = 0.018
    shrink.wrap_mode = 'ABOVE_SURFACE'
    shrink.wrap_method = 'PROJECT'
    shrink.use_project_z = True
    shrink.use_negative_direction = True


class OBJECT_OT_apply_as_decal(Operator):
    bl_idname = 'object.apply_as_decal'
    bl_label = 'IIAP Apply as decal'
    bl_description = 'Apply active image plane as decal to selected object'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        enough = len(context.selected_objects) == 2
        return context.mode == 'OBJECT' and enough

    def execute(self, context):
        apply_as_decal(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


def register():
    from bpy.utils import register_class
    register_class(OBJECT_OT_apply_as_decal)

def unregister():
    from bpy.utils import unregister_class
    unregister_class(OBJECT_OT_apply_as_decal)

if __name__ == "__main__":
    register()
