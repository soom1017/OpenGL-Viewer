import glm

class Node:
    def __init__(self, parent, link_transform_from_parent, shape_transform):
        # hierarchy
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)

        # transform
        self.link_transform_from_parent = link_transform_from_parent
        self.joint_transform = glm.mat4()
        self.global_transform = glm.mat4()
        self.offset = None
        self.endoffset = None

        # shape
        self.shape_transform = shape_transform

    def set_joint_transform(self, joint_transform):
        self.joint_transform = joint_transform
    def set_offset(self, offset):
        self.offset = offset
    def set_endoffset(self, offset):
        self.endoffset = offset

    def update_tree_global_transform(self):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent * self.joint_transform
        else:
            self.global_transform = self.link_transform_from_parent * self.joint_transform

        for child in self.children:
            child.update_tree_global_transform()

    def get_global_transform(self):
        return self.global_transform
    def get_shape_transform(self):
        return self.shape_transform
    def get_offset(self):
        return self.offset
    def get_endoffset(self):
        return self.endoffset