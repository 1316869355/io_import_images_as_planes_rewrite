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
    "name": "Import images as planes rewrite",
    "author": "Florian Meyer (tstscr), mont29, matali, Ted Schundler (SpkyElctrc)",
    "version": (4, 0, 0),
    "blender": (2, 80, 0),
    "location": "Add Mesh Menu - Import Menu - Texture Node Properties - Image Editor > Image",
    "description": "Import images as planes",
    "wiki_url": "",
    "category": "Import-Export",
}

if 'bpy' in locals():
    from importlib import reload
    reload(op_import_images)
    reload(op_arange_objects)
    reload(op_apply_as_decal)
    reload(op_delete_unused_image_datablocks)
    reload(op_delete_unused_material_datablocks)

import bpy

from io_import_images_as_planes_rewrite import op_import_images
from io_import_images_as_planes_rewrite import op_arange_objects
from io_import_images_as_planes_rewrite import op_apply_as_decal
from io_import_images_as_planes_rewrite import op_delete_unused_image_datablocks
from io_import_images_as_planes_rewrite import op_delete_unused_material_datablocks


def register():
    op_import_images.register()
    op_arange_objects.register()
    op_apply_as_decal.register()
    op_delete_unused_image_datablocks.register()
    op_delete_unused_material_datablocks.register()

def unregister():
    op_import_images.unregister()
    op_arange_objects.unregister()
    op_apply_as_decal.unregister()
    op_delete_unused_image_datablocks.unregister()
    op_delete_unused_material_datablocks.unregister()


if __name__ == "__main__":
    register()
