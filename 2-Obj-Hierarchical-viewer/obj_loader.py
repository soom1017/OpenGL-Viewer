import numpy as np
import glm

class Material:
    def __init__(self, filename):
        self.v, self.f, self.vn = self.load_obj(filename)
        self.index_count = len(self.f[0])
        
    def load_obj(self, filename):
        vertexes = []
        faces = [[], [], []]
        normals = []
        try:
            with open(filename) as file:
                for line in file:
                    if line.startswith("v "):
                        v = line.split()[1:]
                        vertexes.append(list(map(float, v)))
                        vertexes.append([1, 1, 1]) # vertex color
                        
                    elif line.startswith("f "):
                        f = line.split()[1:]

                        for face in f:
                            face = face.split('/')
                            for i in range(len(face)):
                                if face[i] != '':
                                    faces[i].append(int(face[i]) - 1)
                        
                    elif line.startswith("vn "):
                        vn = line.split()[1:]
                        normals.append(list(map(float, vn)))
        except IOError:
            print(f"Error: Could not open file {file}")
            return None, None, None
        return vertexes, faces, normals
    
    def get_vertex_pos(self):
        vertex_pos = np.array(self.v, dtype=np.float32)
        vertex_pos = glm.array(vertex_pos)
        return vertex_pos
    
    def get_vertex_indices(self):
        vertex_indices = np.array(self.f[0], dtype=np.uint32)
        vertex_indices = glm.array(vertex_indices)
        return vertex_indices    
    