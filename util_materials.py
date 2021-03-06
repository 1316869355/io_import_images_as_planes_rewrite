import bpy


def hide_socket_toggle(node):
    for socket in node.outputs:
        if not socket.is_linked:
            socket.hide = not socket.hide


def create_nodes_for_material(self, img_spec, material):
    '''return emission material without alpha'''
    img = img_spec.image
    node_tree = material.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    has_alpha = img.depth == 32

    # Start fresh
    for node in nodes:
        nodes.remove(node)

    # Add Nodes
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    if self.materialtype == 'EMISSION':
        main_shader = nodes.new(type='ShaderNodeEmission')
    if self.materialtype == 'DIFFUSE':
        main_shader = nodes.new(type='ShaderNodeBsdfDiffuse')
    if self.materialtype == 'PRINCIPLED':
        main_shader = nodes.new(type='ShaderNodeBsdfPrincipled')

    image_texture = nodes.new(type='ShaderNodeTexImage')
    image_texture.image = img
    image_texture.extension = 'CLIP'

    if img_spec.image.source == 'SEQUENCE':
        image_texture.image_user.frame_start = img_spec.frame_start
        image_texture.image_user.frame_offset = img_spec.frame_offset
        image_texture.image_user.frame_duration = img_spec.frame_duration
        image_texture.image_user.use_auto_refresh = True

    if has_alpha:
        mix = nodes.new(type='ShaderNodeMixShader')
        transparancy = nodes.new(type='ShaderNodeBsdfTransparent')
    if self.only_camera:
        mix2 = nodes.new(type='ShaderNodeMixShader')
        light_path = nodes.new(type='ShaderNodeLightPath')
        if not has_alpha:
            transparancy = nodes.new(type='ShaderNodeBsdfTransparent')

    # Set Locations
    xoffset = material_output.location[0]
    yoffset = material_output.location[1]
    xgap = 365
    ygap = 200
    if has_alpha:
        material.blend_method = 'BLEND'
        img.alpha_mode = self.alpha_mode

        # Locations
        if self.only_camera:
            mix.location = (xoffset - (2 * xgap), yoffset)
            transparancy.location = (
                xoffset - (3 * xgap), yoffset - (ygap / 2))
            main_shader.location = (xoffset - (3 * xgap), yoffset - ygap)
            image_texture.location = (xoffset - (4 * xgap), yoffset)
            mix2.location = (xoffset - (1 * xgap), yoffset)
            light_path.location = (mix.location[0], mix.location[1] + ygap)
        else:
            mix.location = (xoffset - (1 * xgap), yoffset)
            transparancy.location = (
                xoffset - (2 * xgap), yoffset - (ygap / 2))
            main_shader.location = (xoffset - (2 * xgap), yoffset - ygap)
            image_texture.location = (xoffset - (3 * xgap), yoffset)

        # Links
        if self.only_camera:
            links.new(material_output.inputs[0], mix2.outputs[0])
            links.new(mix2.inputs[0], light_path.outputs[0])
            links.new(mix2.inputs[1], transparancy.outputs[0])
            links.new(mix2.inputs[2], mix.outputs[0])
            hide_socket_toggle(light_path)
        else:
            # mix to material_output
            links.new(material_output.inputs[0], mix.outputs[0])
        # transparency to mix
        links.new(mix.inputs[1], transparancy.outputs[0])
        # emmission to mix
        links.new(mix.inputs[2], main_shader.outputs[0])
        # image_texture color to main_shader
        links.new(main_shader.inputs[0], image_texture.outputs[0])
        # image_texture alpha to mix factor
        links.new(mix.inputs[0], image_texture.outputs[1])

    else:
        material.blend_method = 'OPAQUE'

        # Locations
        if self.only_camera:
            main_shader.location = (xoffset - (2 * xgap), yoffset)
            image_texture.location = (xoffset - (3 * xgap), yoffset)
            mix2.location = (xoffset - (1 * xgap), yoffset)
            light_path.location = (
                main_shader.location[0], main_shader.location[1] + ygap)
            transparancy.location = (
                main_shader.location[0], main_shader.location[1] + (ygap / 2))
        else:
            main_shader.location = (xoffset - (1 * xgap), yoffset)
            image_texture.location = (xoffset - (2 * xgap), yoffset)

        # Links
        if self.only_camera:
            links.new(material_output.inputs[0], mix2.outputs[0])
            links.new(mix2.inputs[0], light_path.outputs[0])
            links.new(mix2.inputs[1], transparancy.outputs[0])
            links.new(mix2.inputs[2], main_shader.outputs[0])
            hide_socket_toggle(light_path)
        else:
            # main_shader to material_output
            links.new(material_output.inputs[0], main_shader.outputs[0])
        # image_texture to main_shader
        links.new(main_shader.inputs[0], image_texture.outputs[0])

    # make texture node the active node
    nodes.active = image_texture

    return material


def create_material_for_img_spec(self, img_spec):
    # get existing or create material
    if not self.reuse_existing:
        material = bpy.data.materials.new(img_spec.image.name)
    elif not img_spec.image.name in bpy.data.materials.keys():
        material = bpy.data.materials.new(img_spec.image.name)
    else:
        material = bpy.data.materials[img_spec.image.name]
    material.use_nodes = True

    create_nodes_for_material(self, img_spec, material)

    if self.relative_path:
        # can't always find the relative path (between drive letters on windows)
        try:
            img_spec.image.filepath = bpy.path.relpath(img_spec.image.filepath)
        except ValueError:
            pass

    return material
