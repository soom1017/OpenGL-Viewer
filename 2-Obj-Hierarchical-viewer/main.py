from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from utils import Utils
from vao import prepare_vao_frame, prepare_vao_material
from shader import load_shaders, g_vertex_shader_src, g_fragment_shader_src
from obj_loader import Material

g_material = None
g_vao_material = None

def drag_and_drop_callback(window, paths):
    global g_material, g_vao_material
    g_material = Material(paths[0])
    g_vao_material = prepare_vao_material(g_material)

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

def draw_material(vao, MVP, MVP_loc):
    glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, g_material.index_count, GL_UNSIGNED_INT, None)

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
    utils = Utils()
    glfwSetKeyCallback(window, utils.key_callback)
    glfwSetCursorPosCallback(window, utils.cursor_callback)
    glfwSetMouseButtonCallback(window, utils.button_callback)
    glfwSetScrollCallback(window, utils.scroll_callback)
    glfwSetDropCallback(window, drag_and_drop_callback)

    # load shaders
    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

    # get uniform locations
    MVP_loc = glGetUniformLocation(shader_program, 'MVP')
    
    # prepare vaos
    vao_center_frame = prepare_vao_frame(coordinate_axis=True)
    vao_frame_grid = prepare_vao_frame(coordinate_axis=False)

    # loop until the user closes the window
    while not glfwWindowShouldClose(window):
        # render

        # enable depth test (we'll see details later)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(shader_program)

        # projection & view matrix
        P = utils.get_projection_matrix()
        V = utils.get_view_matrix()

        I = glm.mat4()
        draw_center_frame(vao_center_frame, P*V*I, MVP_loc)
        draw_frame_grid(vao_frame_grid, P*V*I, MVP_loc)
        if g_material:
            draw_material(g_vao_material, P*V*I, MVP_loc)
        

        # swap front and back buffers
        glfwSwapBuffers(window)

        # poll events
        glfwPollEvents()

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    main()