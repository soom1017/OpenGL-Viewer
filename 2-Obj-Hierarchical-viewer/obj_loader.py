import numpy as np
import glm
import os

class Material:
    def __init__(self, filename):
        # print out obj file name
        print(f'obj file name: {os.path.basename(filename)}')
        # get vertex, face information from obj file
        self.vertices = self.load_obj(filename)
        self.vertex_count = len(self.vertices)
        
    def load_obj(self, filename):
        vertices = []

        positions = []
        normals = []

        num_face_tri = 0
        num_face_quad = 0
        num_face_n = 0
        # open and parse obj file contents
        try:
            with open(filename) as file:
                for line in file:
                    # process vertex positions
                    if line.startswith("v "):
                        v = line.split()[1:]
                        positions.append(list(map(float, v)))
                    # process vertex normals
                    elif line.startswith("vn "):
                        vn = line.split()[1:]
                        normals.append(list(map(float, vn)))
                    # process face informations (vertex_pos_idx, texture_coor_idx, vertex_normal_idx)
                    elif line.startswith("f "):
                        f = line.split()[1:]
                        num_vertex = len(f)
                        for idx in range(1, num_vertex - 1):
                            for i in [0, idx, idx+1]:
                                face = f[i].split('/')
                                # face[0]: vertex_pos_idx
                                vertices.append(positions[int(face[0]) - 1])
                                # face[2]: vertex_normal_idx
                                vertices.append(normals[int(face[2]) - 1])
                        # count polygons        
                        if num_vertex == 3:
                            num_face_tri += 1
                        elif num_vertex == 4:
                            num_face_quad += 1
                        else:
                            num_face_n += 1
                    
        except IOError:
            print(f"Error: Could not open file {file}")
            return None, None, None
        # print out face informations
        print(f'total number of faces: {num_face_tri + num_face_quad + num_face_n}')
        print(f'number of faces with 3 vertices: {num_face_tri}')
        print(f'number of faces with 4 vertices: {num_face_quad}')
        print(f'number of faces with more than 4 vertices: {num_face_n}')
        print('----------------------------------------------------------')
        return vertices
    
    def get_vertex_pos_and_normal(self):
        return glm.array(np.array(self.vertices, dtype=np.float32))
    
    def get_vertex_count(self):
        return self.vertex_count // 2