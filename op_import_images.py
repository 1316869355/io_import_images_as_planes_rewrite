'''import images operators'''

import os
import bpy

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import (
    Operator,
    OperatorFileListElement,
)
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import (
    AddObjectHelper,
    object_data_add,
)
from .util_load_images import (
    load_images,
    ImageSpec
)
from .util_materials import (
    create_material_for_img_spec,
)
from .util_mesh import (
    create_mesh,
    set_mesh_verticies
)


def set_select(context, obs):
    for ob in obs:
        ob.select_set(True)

class IIAP_BASE_class:
    """Base Class. Holds all the options."""
    materialtype: EnumProperty(
        name='Material Type',
        items=[
            ('EMISSION', 'Emission', ''),
            ('DIFFUSE', 'Diffuse', ''),
            ('PRINCIPLED', 'Principled', '')
        ],
        description='Set Material Type'
    )
    alpha_mode: EnumProperty(
        name='Alpha Blend Mode',
        items=[
            ('STRAIGHT', 'Straight', ''),
            ('PREMUL', 'Premultiplied', '')
        ],
        description='Alpha blend mode for the image'
    )
    origin: EnumProperty(
        name='Origin Location',
        items=[
            ('CENTER', 'Center', ''),
            ('BL', 'Bottom Left', ''),
            ('BR', 'Bottom Right', ''),
            ('TR', 'Top Right', ''),
            ('TL', 'Top Left', '')
        ],
        description='Set the origin Location'
    )
    only_camera: BoolProperty(
        name='Restrict to Camera Rays',
        default=False,
        description='Set transparent for non-camera rays'
    )
    reuse_existing: BoolProperty(
        name='Reuse existing datablocks',
        default=True,
        description='When re-importing an allready loaded image, re-use existing meshes and materials instead of creating new ones.',
    )
    relative_path: BoolProperty(
        name='Relative Path',
        default=True,
        description='Ensure the path is relative'
    )
    use_sequence: BoolProperty(
        name='Detect Sequences',
        default=True,
        description='Automatically detect animated sequences in selected images'
    )

    def create_mesh_object_for_img_spec(self, context, img_spec):
        # check if mesh with image name allready exists
        NAME = img_spec.image.name
        if not self.reuse_existing:
            mesh = create_mesh(NAME)
        elif not NAME in bpy.data.meshes.keys():
            mesh = create_mesh(NAME)
        else:
            mesh = bpy.data.meshes[NAME]

        set_mesh_verticies(mesh, img_spec.size, self.origin)
        plane_object = object_data_add(context, mesh, operator=self)
        return plane_object

    # Take all image specs and loop over them
    def all_image_specs_to_planes(self, context, image_specs):
        finished_image_planes = []
        for ispec in image_specs:
            image_plane = self.single_image_spec_to_plane(context, ispec)
            finished_image_planes.append(image_plane)

        return finished_image_planes

    # Take image spec give finished plane with material back
    def single_image_spec_to_plane(self, context, img_spec):
        material = create_material_for_img_spec(self, img_spec)
        image_plane = self.create_mesh_object_for_img_spec(context, img_spec)
        image_plane.data.materials.append(material)
        return image_plane


# The Main Import Operator
class IIAP_OT_import_images_as_planes(IIAP_BASE_class, Operator, ImportHelper, AddObjectHelper):
    """Import Images as planes Operator"""
    bl_idname = 'io.import_images_as_planes'
    bl_label = 'Import images as planes'
    bl_description = 'Import images as planes'
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(
        name='Directory',
        subtype='DIR_PATH',
    )
    files: CollectionProperty(
        type=OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    @classmethod
    def poll(cls, context):
        '''only in object mode?'''
        return context.mode == 'OBJECT'

    def execute(self, context):
        '''import image create imageplane'''
        if not self.files:
            print('No Files selected. CANCELLING')
            return {'CANCELLED'}

        # existence check + use name
        filenames = [f.name for f in self.files if os.path.exists(
            os.path.join(self.directory, f.name))]

        # filenames = [f.name for f in files]
        image_specs = load_images(filenames, self.directory, force_reload=True,
                                  frame_start=1, find_sequences=self.use_sequence)
        finished_image_planes = self.all_image_specs_to_planes(
            context, image_specs)

        if not finished_image_planes:
            print('No image planes created. CANCELLING')
            return {'CANCELLED'}

        # Set new Planes as selected
        set_select(context, finished_image_planes)

        if len(finished_image_planes) > 1:
            # Use Arange Grid Operator to lay out
            bpy.ops.object.grid_arange()

        return {'FINISHED'}


def single_image_draw(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    col = layout.column()
    col.prop(self, 'materialtype')
    col.prop(self, 'alpha_mode')
    col.prop(self, 'origin')
    col.prop(self, 'only_camera', toggle=True)
    col.prop(self, 'reuse_existing', toggle=True)

    col.separator()
    # col.prop(self, 'view_align') # Does not do anything. could be a bug
    col.prop(self, 'location')
    # col.prop(self, 'rotation') # Does not do anything. could be a bug


class IIAP_OT_image_to_plane(IIAP_BASE_class, Operator, AddObjectHelper):
    """Create imageplane from one image Operator"""
    bl_idname = 'image.image_to_plane'
    bl_label = 'Plane from image'
    bl_description = 'Create plane with this image'
    bl_options = {'REGISTER', 'UNDO'}

    draw = single_image_draw

    @classmethod
    def poll(cls, context):
        '''In image editor and image is there'''
        # There is no image to work with
        if not context.space_data.type == 'IMAGE_EDITOR' or not context.space_data.image:
            return False
        return True

    def execute(self, context):
        '''imageplane from image in image editor'''
        image = context.space_data.image
        img_spec = ImageSpec(image, image.size, 1, 0, 1, image.use_alpha)
        image_plane = self.single_image_spec_to_plane(context, img_spec)
        set_select(context, [image_plane])

        if not image_plane:
            print('No image plane created. CANCELLING')
            return {'CANCELLED'}
        return {'FINISHED'}


class IIAP_OT_texture_image_to_plane(IIAP_BASE_class, Operator, AddObjectHelper):
    """Create imageplane from texture node image Operator"""
    bl_idname = 'io.texture_image_to_plane'
    bl_label = 'Create Imageplane'
    bl_description = 'Create plane with this image'
    bl_options = {'REGISTER', 'UNDO'}

    draw = single_image_draw

    @classmethod
    def poll(cls, context):
        '''If texture node with image is active'''
        sd = context.space_data
        # There is no image to work with
        if (not sd.type == 'NODE_EDITOR'
                or not sd.node_tree
                or not sd.node_tree.type == 'SHADER'
                or not sd.node_tree.nodes.active
                or not sd.node_tree.nodes.active.bl_idname == 'ShaderNodeTexImage'
                or not sd.node_tree.nodes.active.image):
            return False
        return True

    def execute(self, context):
        '''imageplane from selected texture node'''
        sd = context.space_data
        image = sd.node_tree.nodes.active.image
        img_spec = ImageSpec(image, image.size, 1, 0, 1, image.use_alpha)
        image_plane = self.single_image_spec_to_plane(context, img_spec)
        set_select(context, [image_plane])

        if not image_plane:
            print('No image plane created. CANCELLING')
            return {'CANCELLED'}
        return {'FINISHED'}


# Import Button
def btn_import_images(self, context):
    layout = self.layout
    layout.operator(IIAP_OT_import_images_as_planes.bl_idname, icon='TEXTURE')


# Image Editor Button
def btn_image_to_plane(self, context):
    layout = self.layout
    layout.operator(IIAP_OT_image_to_plane.bl_idname, icon='TEXTURE')


# Node Editor Button
def btn_texture_image_to_plane(self, context):
    layout = self.layout
    if (context.space_data.node_tree.nodes.active.bl_idname == 'ShaderNodeTexImage'
            and context.space_data.node_tree.nodes.active.image):
        layout.separator()
        layout.operator(
            IIAP_OT_texture_image_to_plane.bl_idname, icon='TEXTURE')


def register():
    from bpy.utils import register_class
    register_class(IIAP_OT_import_images_as_planes)
    register_class(IIAP_OT_texture_image_to_plane)
    register_class(IIAP_OT_image_to_plane)

    bpy.types.VIEW3D_MT_image_add.append(btn_import_images)
    bpy.types.VIEW3D_MT_mesh_add.prepend(btn_import_images)
    bpy.types.TOPBAR_MT_file_import.prepend(btn_import_images)
    bpy.types.IMAGE_MT_image.prepend(btn_image_to_plane)
    bpy.types.NODE_PT_active_node_properties.prepend(
        btn_texture_image_to_plane)
    bpy.types.NODE_MT_node.append(btn_texture_image_to_plane)


def unregister():
    from bpy.utils import unregister_class
    unregister_class(IIAP_OT_image_to_plane)
    unregister_class(IIAP_OT_texture_image_to_plane)
    unregister_class(IIAP_OT_import_images_as_planes)

    bpy.types.VIEW3D_MT_image_add.remove(btn_import_images)
    bpy.types.VIEW3D_MT_mesh_add.remove(btn_import_images)
    bpy.types.TOPBAR_MT_file_import.remove(btn_import_images)
    bpy.types.IMAGE_MT_image.remove(btn_image_to_plane)
    bpy.types.NODE_PT_active_node_properties.remove(btn_texture_image_to_plane)
    bpy.types.NODE_MT_node.remove(btn_texture_image_to_plane)


if __name__ == "__main__":
    register()
