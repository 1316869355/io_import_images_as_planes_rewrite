'''import images operators'''

import os

import bmesh
import bpy
from bpy.props import (BoolProperty,  # FloatProperty,; IntProperty,; FloatVectorProperty,
					   CollectionProperty, EnumProperty, StringProperty)
from bpy.types import Operator, OperatorFileListElement
from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Matrix, Vector

BASEVERTS = (
	Vector((-0.5, -0.5, 0)), # bottom left
	Vector((0.5, -0.5, 0)), # bottom right
	Vector((0.5, 0.5, 0)), # top right
	Vector((-0.5, 0.5, 0))) # top left

def set_select(context, obs):
	for ob in obs:
		ob.select_set('SELECT')


def loaded_image(path):
	for img in bpy.data.images:
		if img.filepath_from_user() == path:
			return img
	return None

def exisisting_material(material_name):
	'''return material of material_name if there'''
	for material in bpy.data.materials:
		if material.name == material_name:
			return material
	return None

def existing_mesh(mesh_name):
	'''return mesh of mesh_name if there'''
	for mesh in bpy.data.meshes:
		if mesh.name == mesh_name:
			return mesh
	return None

def delete_nodes_of_bl_idname(nodes, bl_idname):
	'''delete nodes of bl_idname'''
	for node in nodes:
		if node.bl_idname == bl_idname:
			nodes.remove(node)

def return_material_output_node(nodes):
	'''return material output node'''
	for node in nodes:
		if node.bl_idname == 'ShaderNodeOutputMaterial':
			return node
	material_output = nodes.new(type='ShaderNodeOutputMaterial')
	material_output.location = (300, 300)
	return material_output

def create_mesh(img):
	'''create new mesh for img'''
	bm = bmesh.new()
	for v in BASEVERTS:
		bm.verts.new(v)
	bm.verts.ensure_lookup_table()
	bm.faces.new(bm.verts)
	mesh = bpy.data.meshes.new(img.name)
	bm.to_mesh(mesh)
	mesh.uv_layers.new()
	return mesh

def set_mesh_verticies(self, mesh, img):
	'''take mesh and transform to match settings'''
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bm.verts.ensure_lookup_table()

	# Reset to base coordiantes
	for i, v in enumerate(bm.verts):
		v.co = BASEVERTS[i]

	# Scale for x-aspect ratio
	aspect_x = img.size[0] / img.size[1]
	for i, v in enumerate(bm.verts):
		v.co.x = BASEVERTS[i].x * aspect_x

	# Transform according to origin setting
	if not self.origin == 'CENTER':
		print('TRANSLATING')
		if self.origin == 'BL':
			translation = Matrix.Translation(bm.verts[2].co)
			bm.transform(translation)
		elif self.origin == 'BR':
			translation = Matrix.Translation(bm.verts[3].co)
			bm.transform(translation)
		elif self.origin == 'TR':
			translation = Matrix.Translation(bm.verts[0].co)
			bm.transform(translation)
		elif self.origin == 'TL':
			translation = Matrix.Translation(bm.verts[1].co)
			bm.transform(translation)

	bm.to_mesh(mesh)

def create_emission_material(img, material):
	'''return emission material without alpha'''
	node_tree = material.node_tree
	nodes = node_tree.nodes
	links = node_tree.links

	# Set Material Output Node
	material_output = return_material_output_node(nodes)
	# Add Emission Shader
	emmision_shader = nodes.new(type='ShaderNodeEmission')
	emmision_shader.location = (0, 300)
	# Link emmision_shader Output to material_output Input
	links.new(material_output.inputs[0], emmision_shader.outputs[0])
	# Add image texture
	image_texture = nodes.new(type='ShaderNodeTexImage')
	image_texture.image = img
	image_texture.location = (-365, 300)
	# Link image_texture Output to emmision_shader Input
	links.new(emmision_shader.inputs[0], image_texture.outputs[0])
	# make texture node the active node
	nodes.active = image_texture

	return material

def create_diffuse_material(img, material):
	'''return diffuse material without alpha'''
	node_tree = material.node_tree
	nodes = node_tree.nodes
	links = node_tree.links

	# Set Material Output Node
	material_output = return_material_output_node(nodes)
	# Add Emission Shader
	diffuse_shader = nodes.new(type='ShaderNodeBsdfDiffuse')
	diffuse_shader.location = (0, 300)
	# Link diffuse_shader Output to material_output Input
	links.new(material_output.inputs[0], diffuse_shader.outputs[0])
	# Add image texture
	image_texture = nodes.new(type='ShaderNodeTexImage')
	image_texture.image = img
	image_texture.location = (-365, 300)
	# Link image_texture Output to diffuse_shader Input
	links.new(diffuse_shader.inputs[0], image_texture.outputs[0])
	# make texture node the active node
	nodes.active = image_texture

	return material

def create_material(self, img):
	'''take img, return material with image applied'''
	material = exisisting_material(img.name)
	if not material or not self.reuse_existing:
		material = bpy.data.materials.new(img.name)
	material.use_nodes = True
	node_tree = material.node_tree
	# nodes = node_tree.nodes
	# links = node_tree.links

	# Delete all but output Node to start clean
	for node in node_tree.nodes:
		if not node.bl_idname == 'ShaderNodeOutputMaterial':
			node_tree.nodes.remove(node)

	if self.materialtype == 'EMISSION':
		material = create_emission_material(img, material)
	elif self.materialtype == 'DIFFUSE':
		material = create_diffuse_material(img, material)
	return material


def image_plane_generator(self, context, img):
	'''take image, create obj'''
	mesh = existing_mesh(img.name)
	if not mesh or not self.reuse_existing:
		mesh = create_mesh(img)

	set_mesh_verticies(self, mesh, img)

	obj = object_data_add(context, mesh, operator=self)

	material = create_material(self, img)
	### TODO How to do this without operator usage
	if not obj.material_slots:
		bpy.ops.object.material_slot_add()

	obj.material_slots[0].material = material
	return obj

def import_images_as_planes(self, context):
	'''import as planes main function'''
	image_planes = []
	for file in self.files:
		path = os.path.join(self.directory, file.name)

		# Check if file even exists
		if not os.path.exists(path):
			print('Filepath does not exist: %s' %path)
			continue

		# Check if file is usable image even

		# img = loaded_image(path)
		# if not img:
		img = load_image(path, check_existing=True, force_reload=True)

		obj = image_plane_generator(self, context, img)
		image_planes.append(obj)

	return image_planes

def image_to_plane(self, context, path):
	'''take image path, return image plane object'''
	# Check if file even exists
	if not os.path.exists(path):
		print('No image found. Filepath not valid.')
		return None

	# img = loaded_image(path)
	# if not img:
	img = load_image(path, check_existing=True, force_reload=True)

	obj = image_plane_generator(self, context, img)
	return obj

class IIAP_BASE_class:
	"""Base Class. Holds the options for scaling materials, ..."""
	reuse_existing: BoolProperty(
		name='Reuse existing datablocks',
		description='Reuse existing meshes and materials instead of creating new ones.',
		default=True,
	)
	origin: EnumProperty(
		name='Origin Location',
		items=[
			('CENTER', 'Center', ''),
			('BL', 'Bottom Left', ''),
			('BR', 'Bottom Right', ''),
			('TR', 'Top Right', ''),
			('TL', 'Top Left', '')
		]
	)
	materialtype: EnumProperty(
		name='Material Type',
		items=[
			('EMISSION', 'Emission', ''),
			# ('EMISSION_ALPHA', 'Emission BSDF + Alpha', ''),
			('DIFFUSE', 'Diffuse BSDF', ''),
			# ('DIFFUSE_ALPHA', 'Diffuse BSDF + Alpha', ''),
		]
	)


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
		'''should always be possible'''
		return True

	def execute(self, context):
		'''import image create imageplane'''
		print('\nIMPORTING IMAGES')
		print(self.filepath)
		if not self.files:
			print('No Files selected. CANCELLING')
			return {'CANCELLED'}
		image_planes = import_images_as_planes(self, context)
		if not image_planes:
			print('No image planes created. CANCELLING')
			return {'CANCELLED'}
		set_select(context, image_planes)
		print('Created %d image planes' %(len(image_planes)))
		if len(image_planes) > 1:
			bpy.ops.object.grid_arange()
		return {'FINISHED'}




class IIAP_OT_image_to_plane(IIAP_BASE_class, Operator, AddObjectHelper):
	"""Create imageplane from one image Operator"""
	bl_idname = 'image.image_to_plane'
	bl_label = 'Plane from image'
	bl_description = 'Create plane with this image'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		'''In image editor and image is there'''
		# There is no image to work with
		if not context.space_data.type == 'IMAGE_EDITOR' or not context.space_data.image:
			return False
		return True

	def execute(self, context):
		'''imageplane from image in image editor'''
		path = context.space_data.image.filepath_from_user()
		image_plane = image_to_plane(self, context, path)
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
		path = sd.node_tree.nodes.active.image.filepath_from_user()
		image_plane = image_to_plane(self, context, path)
		if not image_plane:
			print('No image plane created. CANCELLING')
			return {'CANCELLED'}
		return {'FINISHED'}
