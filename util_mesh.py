import bpy
import bmesh
from mathutils import Matrix, Vector


BASEVERTS = (
    Vector((-0.5, -0.5, 0)),  # bottom left
    Vector((0.5, -0.5, 0)),  # bottom right
    Vector((0.5, 0.5, 0)),  # top right
    Vector((-0.5, 0.5, 0)))  # top left


def create_mesh(name):
    '''create new mesh with name'''
    bm = bmesh.new()
    for v in BASEVERTS:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()
    bm.faces.new(bm.verts)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    mesh.uv_layers.new()
    return mesh


def set_mesh_verticies(mesh, imagesize, origin):
    '''take mesh and transform to match settings'''
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    # Reset to base coordiantes
    for i, v in enumerate(bm.verts):
        v.co = BASEVERTS[i]

    # Scale for x-aspect ratio
    aspect = imagesize[0] / imagesize[1]
    for i, v in enumerate(bm.verts):
        v.co.x = BASEVERTS[i].x * aspect

    # Transform according to origin setting
    if not origin == 'CENTER':
        # print('TRANSLATING')
        if origin == 'BL':
            translation = Matrix.Translation(bm.verts[2].co)
            bm.transform(translation)
        elif origin == 'BR':
            translation = Matrix.Translation(bm.verts[3].co)
            bm.transform(translation)
        elif origin == 'TR':
            translation = Matrix.Translation(bm.verts[0].co)
            bm.transform(translation)
        elif origin == 'TL':
            translation = Matrix.Translation(bm.verts[1].co)
            bm.transform(translation)

    bm.to_mesh(mesh)
