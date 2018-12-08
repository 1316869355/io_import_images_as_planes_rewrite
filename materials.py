import bpy
from .utils import (
    return_material_output_node,
    hide_socket_toggle,
)

def create_nodes_for_material(self, img, material):
    '''return emission material without alpha'''
    node_tree = material.node_tree
    nodes = node_tree.nodes
    links = node_tree.links
    has_alpha = img.depth == 32

    # Set Material Output Node
    material_output = return_material_output_node(nodes)
    
    # Add Nodes
    if self.materialtype == 'EMISSION':
        main_shader = nodes.new(type='ShaderNodeEmission')
    if self.materialtype == 'DIFFUSE':
        main_shader = nodes.new(type='ShaderNodeBsdfDiffuse')
    if self.materialtype == 'PRINCIPLED':
        main_shader = nodes.new(type='ShaderNodeBsdfPrincipled')

    image_texture = nodes.new(type='ShaderNodeTexImage')
    image_texture.image = img
    if has_alpha:
        mix = nodes.new(type='ShaderNodeMixShader')
        transparancy = nodes.new(type='ShaderNodeBsdfTransparent')
    if self.only_camera:
        mix2 = nodes.new(type='ShaderNodeMixShader')
        light_path = nodes.new(type='ShaderNodeLightPath')
        if not has_alpha:
            transparancy = nodes.new(type='ShaderNodeBsdfTransparent')

    ## Set Locations
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
            transparancy.location = (xoffset - (3 * xgap), yoffset - (ygap / 2))
            main_shader.location = (xoffset - (3 * xgap), yoffset - ygap)
            image_texture.location = (xoffset - (4 * xgap), yoffset)
            mix2.location = (xoffset - (1 * xgap), yoffset)
            light_path.location = (mix.location[0], mix.location[1] + ygap)
        else:
            mix.location = (xoffset - (1 * xgap), yoffset)
            transparancy.location = (xoffset - (2 * xgap), yoffset - (ygap / 2))
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
            light_path.location = (main_shader.location[0], main_shader.location[1] + ygap)
            transparancy.location = (main_shader.location[0], main_shader.location[1] + (ygap / 2))
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

