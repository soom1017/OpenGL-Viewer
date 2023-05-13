from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

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
        self.zoom = 3.
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
        if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
            glfwSetWindowShouldClose(window, GLFW_TRUE);
        else:
            if action==GLFW_PRESS or action==GLFW_REPEAT:
                if key==GLFW_KEY_V:
                    self.is_orthogonal = not self.is_orthogonal

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
