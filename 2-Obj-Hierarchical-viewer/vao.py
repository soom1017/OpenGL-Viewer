from OpenGL.GL import *
import glm
import ctypes

def prepare_vao_frame(coordinate_axis=False):
    # prepare vertex data (in main memory)
    if coordinate_axis:
        vertices = glm.array(glm.float32,
            # position        # color
            -100.0, 0.0, 0.0,  1.0, 0.0, 0.0, # x-axis start
            100.0, 0.0, 0.0,  1.0, 0.0, 0.0, # x-axis end 
            0.0, 0.0, -100.0,  0.0, 1.0, 0.0, # z-axis start
            0.0, 0.0, 100.0,  0.0, 1.0, 0.0, # z-axis end 
        )
    else:
        vertices = glm.array(glm.float32,
            # position        # color
            -100.0, 0.0, 0.0,  0.4, 0.4, 0.4, # x-axis start
            100.0, 0.0, 0.0,  0.4, 0.4, 0.4, # x-axis end 
            0.0, 0.0, -100.0,  0.4, 0.4, 0.4, # z-axis start
            0.0, 0.0, 100.0,  0.4, 0.4, 0.4, # z-axis end 
        )

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def prepare_vao_material(material):
    # prepare vertex data (in main memory)
    vertices = material.get_vertex_pos()
    # prepare index data (in main memory)
    indices = material.get_vertex_indices()

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # create and activate EBO (element buffer object)
    EBO = glGenBuffers(1)   # create a buffer object ID and store it to EBO variable
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)  # activate EBO as an element buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # copy index data to EBO
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy index data to the currently bound element buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    # glEnableVertexAttribArray(1)

    return VAO