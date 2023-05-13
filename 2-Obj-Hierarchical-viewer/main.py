from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from vao import prepare_vao_frame, prepare_vao_material
from shader import load_shaders, g_vertex_shader_src, g_fragment_shader_src
from obj_loader import Material

g_material = None
g_vao_material = None

class Utils:
    def __init__(self) -> None:
        # Manage inputs
        self.mouse_left_down = False
        self.mouse_right_down = False
        self.is_orthogonal = False      # False: perspective (default) / True: orthogonal projection mode
        
        # Variables related to the view, projection
        self.azimuth = 60
        self.elevation = 30
        self.x_orbit_in, self.y_orbit_in = 0., 0.
        self.x_pan_in, self.y_pan_in = 0., 0.
        self.zoom = 5.
        self.pan_vertical, self.pan_horizontal = 0., 0.
        
        self.cam_up = glm.normalize(glm.vec3(- np.sin(np.radians(30)) * np.sin(np.radians(60)), np.cos(np.radians(30)), - np.sin(np.radians(30)) * np.cos(np.radians(60))))
        self.cam_front = -1 * glm.normalize(glm.vec3(np.cos(np.radians(30)) * np.sin(np.radians(60)), np.sin(np.radians(30)), np.cos(np.radians(30)) * np.cos(np.radians(60))))
        self.cam_target = self.cam_up * self.pan_vertical * .1 + glm.cross(self.cam_front, self.cam_up) * self.pan_horizontal * .1
        
    def get_view_matrix(self):
        V = glm.lookAt(self.cam_target - self.cam_front * self.zoom, self.cam_target, self.cam_up)
        return V
    
    def get_projection_matrix(self):
        width, height = 3200, 3200
        glViewport(0, 0, width, height)

        if self.is_orthogonal:
            ortho_height = 10.
            ortho_width = ortho_height * width/height
            P = glm.ortho(-ortho_width*.5,ortho_width*.5, -ortho_height*.5,ortho_height*.5, -10,10)
        else:
            aspect = width / height
            P = glm.perspective(glm.radians(45), aspect, 1, 10)
        return P

    def key_callback(self, window, key, scancode, action, mods):
        global g_material
        if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
            glfwSetWindowShouldClose(window, GLFW_TRUE);
        else:
            if action==GLFW_PRESS or action==GLFW_REPEAT:
                if key==GLFW_KEY_V:
                    self.is_orthogonal = not self.is_orthogonal
                if key==GLFW_KEY_H:
                    g_material = None
                if key==GLFW_KEY_1:
                    print(f"self.cam_front: {self.cam_target - self.cam_front * self.zoom}, self.cam_target: {self.cam_target}, self.cam_up: {self.cam_up}")

    def cursor_callback(self, window, xpos, ypos):
        # Orbit: Rotate the camera around the target point.
        if self.mouse_left_down:
            self.azimuth -= (xpos - self.x_orbit_in)*0.05
            self.elevation += (ypos - self.y_orbit_in)*0.05
            self.x_orbit_in, self.y_orbit_in = xpos, ypos
            
            azi = np.radians(self.azimuth)
            ele = np.radians(self.elevation)
            self.cam_up = glm.normalize(glm.vec3(- np.sin(ele) * np.sin(azi), np.cos(ele), - np.sin(ele) * np.cos(azi)))
            self.cam_front = -1 * glm.normalize(glm.vec3(np.cos(ele) * np.sin(azi), np.sin(ele), np.cos(ele) * np.cos(azi)))

        # Pan: Move both the target point and camera.
        if self.mouse_right_down:
            self.pan_horizontal -= (xpos - self.x_pan_in) * 0.05
            self.pan_vertical += (ypos - self.y_pan_in) * 0.05
            self.x_pan_in, self.y_pan_in = xpos, ypos
            
            self.cam_target = self.cam_up * self.pan_vertical * .1 + glm.cross(self.cam_front, self.cam_up) * self.pan_horizontal * .1

    def button_callback(self, window, button, action, mod):
        if button==GLFW_MOUSE_BUTTON_LEFT:
            if action==GLFW_PRESS:
                self.mouse_left_down = True
                self.x_orbit_in, self.y_orbit_in = glfwGetCursorPos(window)
            elif action==GLFW_RELEASE:
                self.mouse_left_down = False

        elif button==GLFW_MOUSE_BUTTON_RIGHT:
            if action==GLFW_PRESS:
                self.mouse_right_down = True
                self.x_pan_in, self.y_pan_in = glfwGetCursorPos(window)
            elif action==GLFW_RELEASE:
                self.mouse_right_down = False
        
    def scroll_callback(self, window, xoffset, yoffset):
        # Zoom: Move the camera forward the target point (zoom in) and backward away from the target point (zoom out).
        self.zoom = max(self.zoom - yoffset * .1, 1.)

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