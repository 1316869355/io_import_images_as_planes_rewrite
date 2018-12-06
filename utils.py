
def return_material_output_node(nodes):
    '''return material output node'''
    for node in nodes:
        if node.bl_idname == 'ShaderNodeOutputMaterial':
            return node
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (300, 300)
    return material_output

def hide_socket_toggle(node):
    for socket in node.outputs:
        if not socket.is_linked:
            socket.hide = not socket.hide