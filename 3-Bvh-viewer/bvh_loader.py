import os

def load_bvh(filename):
    # open and parse bvh file contents
    motion_data = False
    end_site = False
    channel_str_to_idx = {'XPOSITION': 0, 'YPOSITION': 1, 'ZPOSITION': 2, 
                          'XROTATION': 0, 'YROTATION': 1, 'ZROTATION': 2}
    parents = []        # stack, to store child idx in parent node
    current_idx = 0
    
    data = {
        "Joints": [
            # {
            #     "name": node name,
            #     "child": [],
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
                        data["Motions"].append(values)
                    continue
                # HIERARCHY
                if "JOINT" in line or "ROOT" in line:
                    data["Joints"].append({
                        "name": values[-1],
                        "child": []
                    })
                    if parents:
                        data["Joints"][parents[-1]]["child"].append(current_idx)
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