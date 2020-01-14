from PIL import Image
from OpenGL.GL import glBindTexture, glTexParameteri, glTexImage2D
from OpenGL.GL import GL_TEXTURE_2D, GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_TEXTURE_WRAP_R
from OpenGL.GL import GL_UNSIGNED_BYTE, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_RGB, GL_RGBA
from OpenGL.GL import GL_TEXTURE_CUBE_MAP_POSITIVE_X, GL_CLAMP_TO_EDGE, GL_REPEAT


def load_texture(path, textureID):
    glBindTexture(GL_TEXTURE_2D, textureID)
    # load image
    image = Image.open(path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = image.convert("RGBA").tobytes()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    # Parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return textureID


def load_cubemap(paths, textureID):
    glBindTexture(GL_TEXTURE_CUBE_MAP, textureID)
    # load image
    for i, path in enumerate(paths):
        image = Image.open(path)
        # image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGB").tobytes()
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, image.width, image.height,
                     0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    # Parameters
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    return textureID
