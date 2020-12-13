import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr
from PIL import Image

vertex_src = """
#version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;

uniform mat4 model; // combined rotation and translation
uniform mat4 projection; 


out vec2 v_texture;
void main()
{
    gl_Position = projection * model * vec4(a_position, 1.0); 
    v_texture = a_texture;
}
"""
fragment_src = """
#version 330 core

in vec3 v_color;
in vec2 v_texture;

out vec4 out_color;

uniform sampler2D s_texture;

void main()
{
    out_color = texture(s_texture, v_texture); 
}
"""



def window_resize(window, width, height):
    glViewport(0,0,width,height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, width/height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)



# CONSTANTS
win_w = 1280
win_h = 720
win_pos_x = 400
win_pos_y = 200
X_ROTATION = 0.5
Y_ROTATION = 0.5



print ('===========================')
if not glfw.init():
    raise Exception("Could not initialize glfw")
else:
    print ('glfw initialized')
print ('===========================')



# CREATING WINDOW 
window = glfw.create_window(win_w,win_h,"Test", None, None)
print ('===========================')
if not window:
    glfw.terminate()
    raise Exception("Window not created")
else:
    print('Window created')
print ('===========================')
print('')

glfw.set_window_pos(window,400,200)
glfw.set_window_size_callback(window, window_resize)
glfw.make_context_current(window)




####### WORKSPACE ########



vertices = [-0.5,-0.5, 0.5,  0.0, 0.0,
             0.5,-0.5, 0.5,  1.0, 0.0,
             0.5, 0.5, 0.5,  1.0, 1.0,
            -0.5, 0.5, 0.5,  0.0, 1.0,
             #
            -0.5,-0.5,-0.5,  0.0, 0.0,
             0.5,-0.5,-0.5,  1.0, 0.0,
             0.5, 0.5,-0.5,  1.0, 1.0,
            -0.5, 0.5,-0.5,  0.0, 1.0,
             #
             0.5,-0.5,-0.5,  0.0, 0.0,
             0.5, 0.5,-0.5,  1.0, 0.0,
             0.5, 0.5, 0.5,  1.0, 1.0,
             0.5,-0.5, 0.5,  0.0, 1.0,
             #
            -0.5, 0.5,-0.5,  0.0, 0.0,
            -0.5,-0.5,-0.5,  1.0, 0.0,
            -0.5,-0.5, 0.5,  1.0, 1.0,
            -0.5, 0.5, 0.5,  0.0, 1.0,
             #
            -0.5,-0.5,-0.5,  0.0, 0.0,
             0.5,-0.5,-0.5,  1.0, 0.0,
             0.5,-0.5, 0.5,  1.0, 1.0,
            -0.5,-0.5, 0.5,  0.0, 1.0,
             #
             0.5, 0.5,-0.5,  0.0, 0.0,
            -0.5, 0.5,-0.5,  1.0, 0.0,
            -0.5, 0.5, 0.5,  1.0, 1.0,
             0.5, 0.5, 0.5,  0.0, 1.0]
vertices = np.array(vertices, dtype=np.float32)

indicies = [ 0,  1,  2,  2,  3,  0,
             4,  5,  6,  6,  7,  4,
             8,  9, 10, 10, 11,  8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20]
indicies = np.array(indicies, dtype=np.uint32)

shader = compileProgram(compileShader(vertex_src,GL_VERTEX_SHADER), compileShader(fragment_src,GL_FRAGMENT_SHADER))

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indicies.nbytes, indicies, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(12))

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)

glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_REPEAT)

glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER, GL_LINEAR)

image = Image.open("D:/CG/CGtex/cmc.jpg")
image = image.transpose(Image.FLIP_TOP_BOTTOM)

img_data = image.convert("RGBA").tobytes()
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

glUseProgram(shader)
glClearColor(0.1,0.2,0.3,1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, win_w/win_h, 0.1, 100)
translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, -3]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
####### WORKSPACE ########



# RENDER LOOP
while not glfw.window_should_close(window):
    glfw.poll_events()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
   
    rot_x = pyrr.Matrix44.from_x_rotation(X_ROTATION * glfw.get_time())
    rot_y = pyrr.Matrix44.from_y_rotation(Y_ROTATION * glfw.get_time())

    rotation = pyrr.matrix44.multiply(rot_x,rot_y)
    model = pyrr.matrix44.multiply(rotation,translation)

    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)


    glDrawElements(GL_TRIANGLES, len(indicies), GL_UNSIGNED_INT, None)

    glfw.swap_buffers(window)



glfw.terminate()
