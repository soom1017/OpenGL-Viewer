import numpy as np
import glm
import os

class Material:
    def __init__(self, filename):
        # print out obj file name
        print(f'obj file name: {os.path.basename(filename)}')
        # get vertex, face information from obj file
        self.v, self.f, self.vn = self.load_obj(filename)
        self.index_count = len(self.f[0])
        
    def load_obj(self, filename):
        vertexes = []
        faces = [[], [], []]
        normals = []

        num_face_tri = 0
        num_face_quad = 0
        num_face_n = 0
        try:
            with open(filename) as file:
                for line in file:
                    if line.startswith("v "):
                        v = line.split()[1:]
                        vertexes.append(list(map(float, v)))
                        # vertexes.append([1, 1, 1]) # vertex color
                        
                    elif line.startswith("f "):
                        f = line.split()[1:]
                        num_vertex = len(f)
                        for idx in range(1, num_vertex - 1):
                            for i in [0, idx, idx+1]:
                                face = f[i].split('/')
                                for j in range(len(face)):
                                    if face[j] != '':
                                        faces[j].append(int(face[j]) - 1)
                        if num_vertex == 3:
                            num_face_tri += 1
                        elif num_vertex == 4:
                            num_face_quad += 1
                        else:
                            num_face_n += 1

                    elif line.startswith("vn "):
                        vn = line.split()[1:]
                        normals.append(list(map(float, vn)))
        except IOError:
            print(f"Error: Could not open file {file}")
            return None, None, None
        # print out face informations
        print(f'total number of faces: {num_face_tri + num_face_quad + num_face_n}')
        print(f'number of faces with 3 vertices: {num_face_tri}')
        print(f'number of faces with 4 vertices: {num_face_quad}')
        print(f'number of faces with more than 4 vertices: {num_face_n}')
        print('----------------------------------------------------------')
        return vertexes, faces, normals
    
    def get_vertex_pos(self):
        vertex_pos = np.array(self.v, dtype=np.float32)
        vertex_pos = glm.array(vertex_pos)
        return vertex_pos
    
    def get_vertex_indices(self):
        vertex_indices = np.array(self.f[0], dtype=np.uint32)
        vertex_indices = glm.array(vertex_indices)
        return vertex_indices    
    