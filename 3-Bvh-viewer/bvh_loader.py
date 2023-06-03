import os
import glm
from hierarchy import Node

def load_bvh(filename):
    # open and parse bvh file contents
    motion_data = False
    end_site = False
    channel_str_to_idx = {'XPOSITION': 0, 'YPOSITION': 1, 'ZPOSITION': 2, 
                          'XROTATION': glm.vec3(1, 0, 0), 'YROTATION': glm.vec3(0, 1, 0), 'ZROTATION': glm.vec3(0, 0, 1)}
    parents = []        # stack, to store parent idx in child
    current_idx = 0
    
    data = {
        "Joints": [
            # {
            #     "name": node name,
            #     "parent": parent node idx (if root, None),
            #     "offset": [],
            #     "channels": [],
            #     "endoffset": [],
            # }
        ],
        "Motions": []
    }
    num_frames = 0
    frame_time = 0

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

            for line in lines:
                line = line.strip()
                if not line or line.startswith(('//', '#')):
                    continue
                if "HIERARCHY" in line:
                    continue
                if "MOTION" in line:
                    motion_data = True
                    continue

                values = line.split()
                # MOTION
                if motion_data:
                    if line.startswith("Frames:"):
                        num_frames = int(values[-1])
                    elif line.startswith("Frame Time:"):
                        frame_time = float(values[-1])
                    else:
                        data["Motions"].append(list(map(float, values)))
                    continue
                # HIERARCHY
                if "JOINT" in line or "ROOT" in line:
                    data["Joints"].append({
                        "name": values[-1],
                        "parent": None,
                        "endoffset": None,
                        "offset": None,
                        "channels": None
                    })
                    if parents:
                        data["Joints"][-1]["parent"] = parents[-1]
                    parents.append(current_idx)
                    current_idx += 1

                elif "OFFSET" in line:
                    if end_site:
                        data["Joints"][-1]["endoffset"] = list(map(float, values[1:]))
                    else:
                        data["Joints"][-1]["offset"] = list(map(float, values[1:]))
                elif "CHANNELS" in line:
                    data["Joints"][-1]["channels"] = list(map(lambda x: channel_str_to_idx[x], values[2:]))
                elif "End Site" in line:
                    end_site = True
                elif "}" in line:
                    if end_site:
                        end_site = False
                    else:
                        parents.pop()
                
        return data, num_frames, frame_time

    except IOError:
        print(f"Error: Could not open file {file}")

    return None, None, None
        
class Character:
    def __init__(self, filename):
        # print out bvh file name
        print(f'bvh file name: {os.path.basename(filename)}')

        # load and get information from bvh file
        self.data, self.num_frames, self.frame_time = load_bvh(filename)
        if not self.num_frames:
            print(f"Error: no frame information exists")
            return
        self.joints = list(x["name"] for x in self.data["Joints"])
    
        # print out face informations
        print(f'number of frames: {self.num_frames}')
        print(f'fps: {1 / self.frame_time : .4f}')
        print(f'number of joints: {len(self.joints)}')
        print(f'list of all joint names: {self.joints}')
        print('----------------------------------------')

        # create a hirarchical model - Node(parent, link_transform_from_parent, shape_transform)
        self.nodes = []
        for idx, joint in enumerate(self.data["Joints"]):
            xoff, yoff, zoff = joint["offset"]
            channels = joint["channels"]

            if joint["parent"] == None:         # ROOT
                xpos = self.data["Motions"][0][idx+channels[0]]
                ypos = self.data["Motions"][0][idx+channels[1]]
                zpos = self.data["Motions"][0][idx+channels[2]]
                ang1 = glm.radians(self.data["Motions"][0][idx+3])
                ang2 = glm.radians(self.data["Motions"][0][idx+4])
                ang3 = glm.radians(self.data["Motions"][0][idx+5])
                node = Node(None, 
                            glm.translate((xpos, ypos, zpos)) * glm.rotate(ang1, channels[3]) * glm.rotate(ang2, channels[4]) * glm.rotate(ang3, channels[5]), 
                            glm.scale((.01, .01, .01)))
            else:
                ang1 = glm.radians(self.data["Motions"][0][idx+0])
                ang2 = glm.radians(self.data["Motions"][0][idx+1])
                ang3 = glm.radians(self.data["Motions"][0][idx+2])
                # local frame의 x축을 (xoff, yoff, zoff)와 같아지게 회전
                x_axis = glm.vec3(1,0,0)
                point = glm.vec3(xoff, yoff, zoff)
                dist = glm.distance(point, glm.vec3())
                ang = glm.acos(glm.dot(x_axis, glm.normalize(point)))
                axis = glm.normalize(glm.cross(x_axis, point))
                R = glm.rotate(glm.mat4(1.0), ang, axis)
                node = Node(self.nodes[joint["parent"]],
                            glm.translate((xoff, yoff, zoff)) * glm.rotate(ang1, channels[0]) * glm.rotate(ang2, channels[1]) * glm.rotate(ang3, channels[2]),
                            glm.scale((0.01, 0.01, 0.01)))
            self.nodes.append(node)
        # recursively update global transformations of all nodes
        self.nodes[0].update_tree_global_transform()

    def get_nodes(self):
        return self.nodes