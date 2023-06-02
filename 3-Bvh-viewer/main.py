from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np
import os

from vao import prepare_vao_frame, prepare_vao_material
from shader import load_shaders, g_vertex_shader_src, g_fragment_shader_src
from bvh_loader import Character
from hierarchy import Node

PROJECT_DIR = os.path.dirname( os.path.abspath( __file__ ) )

g_my_character = None
g_vao_single_material = None
g_hierarchical_mode = False
g_wireframe_mode = False

# Manage inputs
g_mouse_left_down = False
g_mouse_right_down = False
g_is_orthogonal = False      # False: perspective (default) / True: orthogonal projection mode

# Variables related to the view, projection
g_azimuth = 60
g_elevation = 30
g_x_orbit_in, g_y_orbit_in = 0., 0.
g_x_pan_in, g_y_pan_in = 0., 0.
g_zoom = 3.
g_pan_vertical, g_pan_horizontal = 0., 0.

g_cam_up = glm.normalize(glm.vec3(- np.sin(np.radians(30)) * np.sin(np.radians(60)), np.cos(np.radians(30)), - np.sin(np.radians(30)) * np.cos(np.radians(60))))
g_cam_front = -1 * glm.normalize(glm.vec3(np.cos(np.radians(30)) * np.sin(np.radians(60)), np.sin(np.radians(30)), np.cos(np.radians(30)) * np.cos(np.radians(60))))
g_cam_target = g_cam_up * g_pan_vertical * .1 + glm.cross(g_cam_front, g_cam_up) * g_pan_horizontal * .1
        
def get_view_matrix():
    view_pos = g_cam_target - g_cam_front * g_zoom
    V = glm.lookAt(view_pos, g_cam_target, g_cam_up)
    return view_pos, V
    
def get_projection_matrix():
    width, height = 3200, 3200

    if g_is_orthogonal:
        ortho_height = 10.
        ortho_width = ortho_height * width/height
        P = glm.ortho(-ortho_width*.5,ortho_width*.5, -ortho_height*.5,ortho_height*.5, -10,10)
    else:
        aspect = width / height
        P = glm.perspective(45, aspect, 1, 20)
    return P

# callbacks
def key_callback(window, key, scancode, action, mods):
    global g_is_orthogonal, g_single_material, g_hierarchical_mode, g_wireframe_mode
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE);
    else:
        if action==GLFW_PRESS or action==GLFW_REPEAT:
            if key==GLFW_KEY_V:
                g_is_orthogonal = not g_is_orthogonal
            if key==GLFW_KEY_H:
                g_single_material = None
                g_hierarchical_mode = True
            if key==GLFW_KEY_Z:
                g_wireframe_mode = not g_wireframe_mode
            if key==GLFW_KEY_1:
                print(f"g_cam_front: {g_cam_target - g_cam_front * g_zoom}, g_cam_target: {g_cam_target}, g_cam_up: {g_cam_up}")

def cursor_callback(window, xpos, ypos):
    global g_azimuth, g_elevation, g_pan_horizontal, g_pan_vertical, g_cam_up, g_cam_front, g_cam_target, g_x_orbit_in, g_y_orbit_in, g_x_pan_in, g_y_pan_in
    # Orbit: Rotate the camera around the target point.
    if g_mouse_left_down:
        g_azimuth -= (xpos - g_x_orbit_in)*0.05
        g_elevation += (ypos - g_y_orbit_in)*0.05
        g_x_orbit_in, g_y_orbit_in = xpos, ypos
        
        azi = np.radians(g_azimuth)
        ele = np.radians(g_elevation)
        g_cam_up = glm.normalize(glm.vec3(- np.sin(ele) * np.sin(azi), np.cos(ele), - np.sin(ele) * np.cos(azi)))
        g_cam_front = -1 * glm.normalize(glm.vec3(np.cos(ele) * np.sin(azi), np.sin(ele), np.cos(ele) * np.cos(azi)))

    # Pan: Move both the target point and camera.
    if g_mouse_right_down:
        g_pan_horizontal -= (xpos - g_x_pan_in) * 0.05
        g_pan_vertical += (ypos - g_y_pan_in) * 0.05
        g_x_pan_in, g_y_pan_in = xpos, ypos
        
        g_cam_target = g_cam_up * g_pan_vertical * .1 + glm.cross(g_cam_front, g_cam_up) * g_pan_horizontal * .1

def button_callback(window, button, action, mod):
    global g_mouse_left_down, g_mouse_right_down, g_x_orbit_in, g_y_orbit_in, g_x_pan_in, g_y_pan_in
    if button==GLFW_MOUSE_BUTTON_LEFT:
        if action==GLFW_PRESS:
            g_x_orbit_in, g_y_orbit_in = glfwGetCursorPos(window)
            g_mouse_left_down = True
        elif action==GLFW_RELEASE:
            g_mouse_left_down = False

    elif button==GLFW_MOUSE_BUTTON_RIGHT:
        if action==GLFW_PRESS:
            g_x_pan_in, g_y_pan_in = glfwGetCursorPos(window)
            g_mouse_right_down = True
        elif action==GLFW_RELEASE:
            g_mouse_right_down = False
    
def scroll_callback(window, xoffset, yoffset):
    global g_zoom
    # Zoom: Move the camera forward the target point (zoom in) and backward away from the target point (zoom out).
    g_zoom = max(g_zoom - yoffset * .1, 1.)

def drag_and_drop_callback(window, paths):
    global g_my_character
    if not paths[0].endswith('.bvh'):
        print("Error: file extension must be (.bvh)")
        print("------------------------------------")
        return
    g_my_character = Character(paths[0])
    # g_vao_single_material = prepare_vao_material(g_single_material)

# draw functions
def draw_center_frame(vao, MVP, MVP_loc):
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
    glBindVertexArray(vao)
    glDrawArrays(GL_LINES, 0, 4)

def draw_frame_grid(vao, MVP, MVP_loc):
    for i in range(-1000, 1000):
        if i == 0:
            continue

        T = glm.translate(glm.vec3(0.1*i, 0., 0.))
        MVP_z = MVP*T
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP_z))
        glBindVertexArray(vao)
        glDrawArrays(GL_LINES, 2, 4)

        T = glm.translate(glm.vec3(0., 0., 0.1*i))
        MVP_x = MVP*T
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP_x))
        glBindVertexArray(vao)
        glDrawArrays(GL_LINES, 0, 2)

def draw_single_material(vao, VP, unif_locs):
    # scale sample single meshes to smaller size
    M = glm.scale((0.5, 0.5, 0.5))
    MVP = VP * M

    glBindVertexArray(vao)
    # set uniform values
    glUniformMatrix4fv(unif_locs['M'], 1, GL_FALSE, glm.value_ptr(M))
    glUniformMatrix4fv(unif_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
    glUniform3f(unif_locs['material_color'], 1, 1, 1)
    
    glDrawArrays(GL_TRIANGLES, 0, g_single_material.get_vertex_count())

def draw_node(vao, node, vertex_count, VP, unif_locs):
    # apply global transform to node's transform
    M = node.get_global_transform() * node.get_shape_transform()
    MVP = VP * M
    color = node.get_color()

    glBindVertexArray(vao)
    # set uniform values
    glUniformMatrix4fv(unif_locs['M'], 1, GL_FALSE, glm.value_ptr(M))
    glUniformMatrix4fv(unif_locs['MVP'], 1, GL_FALSE, glm.value_ptr(MVP))
    glUniform3f(unif_locs['material_color'], color.r, color.g, color.b)
    
    glDrawArrays(GL_TRIANGLES, 0, vertex_count)

# main function
def main():
    # initialize glfw
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

    # create a window and OpenGL context
    window = glfwCreateWindow(1600, 1600, '2020057692', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    # register event callbacks
    glfwSetKeyCallback(window, key_callback)
    glfwSetCursorPosCallback(window, cursor_callback)
    glfwSetMouseButtonCallback(window, button_callback)
    glfwSetScrollCallback(window, scroll_callback)
    glfwSetDropCallback(window, drag_and_drop_callback)

    # load shaders
    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

    # get uniform locations
    MVP_loc_frame = glGetUniformLocation(shader_program, 'MVP')

    # load materials for hierarchical model
    # tray = Material(os.path.join(PROJECT_DIR, 'obj_files', 'Tray.obj'))
    # spinning_top1 = Material(os.path.join(PROJECT_DIR, 'obj_files', 'Top_jack.obj'))
    # spinning_top2 = Material(os.path.join(PROJECT_DIR, 'obj_files', 'Jack_in_the_Box.obj'))
    # sword = Material(os.path.join(PROJECT_DIR, 'obj_files', 'Sword.obj'))

    # prepare vaos
    vao_center_frame = prepare_vao_frame(coordinate_axis=True)
    vao_frame_grid = prepare_vao_frame(coordinate_axis=False)
    # vao_tray = prepare_vao_material(tray)
    # vao_spinning_top1 = prepare_vao_material(spinning_top1)
    # vao_spinning_top2 = prepare_vao_material(spinning_top2)
    # vao_sword = prepare_vao_material(sword)

    # # create a hierarchical model - Node(parent, shape_transform, color)
    # node_base = Node(None, glm.rotate(np.radians(270), (1, 0, 0)) * glm.scale((.3, .3, .3)), glm.vec3(0,0,0.5))
    # node_spinning_top1 = Node(node_base, glm.translate((-1.05,0.1,0.7)) * glm.rotate(np.radians(270), (1, 0, 0)) * glm.scale((.1, .1, .1)), glm.vec3(0.9294, 0.6745, 0.6941))
    # node_spinning_top2 = Node(node_base, glm.translate((0.3,0.08,-0.1)) * glm.scale((.25, .25, .25)), glm.vec3(0.2902, 0.6588, 0.8471))
    # nodes_sword = []
    # for i in range(3):
    #     node_sword = Node(node_spinning_top1, glm.rotate(np.radians(90), (1, 0, 0)) * glm.scale((0.008, 0.008, 0.008)), glm.vec3(1, 0, 0))
    #     nodes_sword.append(node_sword)
    # for i in range(3):
    #     node_sword = Node(node_spinning_top2, glm.rotate(np.radians(90), (1, 0, 0)) * glm.scale((0.008, 0.008, 0.008)), glm.vec3(1, 0, 0))
    #     nodes_sword.append(node_sword)

    # loop until the user closes the window
    while not glfwWindowShouldClose(window):
        # enable depth test (we'll see details later)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(shader_program)

        # projection & view matrix
        P = get_projection_matrix()
        view_pos, V = get_view_matrix()

        M = glm.mat4()
        draw_center_frame(vao_center_frame, P*V*M, MVP_loc_frame)
        draw_frame_grid(vao_frame_grid, P*V*M, MVP_loc_frame)

        # if g_single_material:
        #     pass
        # elif g_hierarchical_mode:
        #     t = glfwGetTime()

            # # set local transformations of each node
            # node_base.set_transform(glm.rotate(np.radians(np.sin(t) * 30), (1,0,0)))
            # node_spinning_top1.set_transform(glm.rotate(t * 1, (0,1,0)) * glm.translate((np.sin(t) * 0.4, 0, np.sin(t) * 0.4)) * glm.rotate(t * 1, (0,1,0)))
            # node_spinning_top2.set_transform(glm.rotate(t * 2, (0,1,0)) * glm.translate((np.cos(t) * 0.8, 0, np.cos(t) * 0.8)) * glm.rotate(t * 2, (0,1,0)))
            # for i in range(6):
            #     sign1 = 1 if i % 2 == 0 else -1
            #     sign2 = 1 if i % 3 == 0 else -1
            #     nodes_sword[i].set_transform(glm.translate((sign1 * 0.15, 0.8 + sign1 * np.sin(t * 5) * 0.1, sign1 * sign2 * 0.15)))

            # # recursively update global transformations of all nodes
            # node_base.update_tree_global_transform()
            
            # draw_node(vao_tray, node_base, tray.get_vertex_count(), P*V, unif_locs_mat)
            # draw_node(vao_spinning_top1, node_spinning_top1, spinning_top1.get_vertex_count(), P*V, unif_locs_mat)
            # draw_node(vao_spinning_top2, node_spinning_top2, spinning_top2.get_vertex_count(), P*V, unif_locs_mat)
            # for i in range(6):
            #     draw_node(vao_sword, nodes_sword[i], sword.get_vertex_count(), P*V, unif_locs_mat)

        # swap front and back buffers
        glfwSwapBuffers(window)

        # poll events
        glfwPollEvents()

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    main()