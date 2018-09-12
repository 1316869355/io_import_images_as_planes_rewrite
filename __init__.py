# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Import images as planes",
    "author": "Florian Meyer (tstscr), mont29, matali, Ted Schundler (SpkyElctrc)",
    "version": (4, 0, 0),
    "blender": (2, 80, 0),
    "location": "Add Mesh Menu -- Import Menu -- Texture Node Properties -- Image Editor > Image",
    "description": "Import images as planes",
    "wiki_url": "",
    "category": "Import-Export",
}

if 'bpy' in locals():
    from importlib import reload
    reload(op_import_images)
    reload(op_delete_unused_image_datablocks)
    reload(op_delete_unused_material_datablocks)

import bpy

from io_import_images_as_planes import op_import_images
from io_import_images_as_planes import op_delete_unused_image_datablocks
from io_import_images_as_planes import op_delete_unused_material_datablocks

def btn_import_images(self, context):
    layout = self.layout
    layout.operator(op_import_images.IIAP_OP_import_images_as_planes.bl_idname)

def btn_image_to_plane(self, context):
    layout = self.layout
    layout.operator(op_import_images.IIAP_OP_image_to_plane.bl_idname)

def btn_texture_image_to_plane(self, context):
    layout = self.layout
    if (context.space_data.node_tree.nodes.active.bl_idname == 'ShaderNodeTexImage'
    and context.space_data.node_tree.nodes.active.image):
        layout.separator()
        layout.operator(op_import_images.IIAP_OP_texture_image_to_plane.bl_idname)

classes = (
    op_import_images.IIAP_OP_import_images_as_planes,
    op_import_images.IIAP_OP_image_to_plane,
    op_import_images.IIAP_OP_texture_image_to_plane,
    op_delete_unused_image_datablocks.IIAP_OP_delete_unused_image_datablocks,
    op_delete_unused_material_datablocks.IIAP_OP_delete_unused_image_datablocks
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.INFO_MT_mesh_add.prepend(btn_import_images)
    bpy.types.INFO_MT_file_import.prepend(btn_import_images)
    bpy.types.IMAGE_MT_image.prepend(btn_image_to_plane)
    bpy.types.NODE_PT_active_node_properties.prepend(btn_texture_image_to_plane)
    bpy.types.NODE_MT_node.append(btn_texture_image_to_plane)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.INFO_MT_mesh_add.remove(btn_import_images)
    bpy.types.INFO_MT_file_import.remove(btn_import_images)
    bpy.types.IMAGE_MT_image.remove(btn_image_to_plane)
    bpy.types.NODE_PT_active_node_properties.remove(btn_texture_image_to_plane)
    bpy.types.NODE_MT_node.remove(btn_texture_image_to_plane)

if __name__ == "__main__":
    register()
