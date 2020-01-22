from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class ShaderLoader:
    def __init__(self, vs_path, fs_path):
        self.vs_data, self.fs_data = self.__load_shaders(vs_path, fs_path)

    def __load_shaders(self, vs_path, fs_path):
        with open(vs_path) as vs, open(fs_path) as fs:
            vs_data = vs.read()
            fs_data = fs.read()
        return vs_data, fs_data

    def get_compiled_shader(self):
        shader = compileProgram(compileShader(self.vs_data, GL_VERTEX_SHADER),
                                compileShader(self.fs_data, GL_FRAGMENT_SHADER))
        return shader
