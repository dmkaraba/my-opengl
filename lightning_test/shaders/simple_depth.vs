#version 330 core
layout (location = 0) in vec3 position;

uniform mat4 lightSpaceMatrix;
uniform mat4 model;

void main()
{
    // This vertex shader takes a per-object model, a vertex
    // and transforms all vertices to light space using lightSpaceMatrix
    gl_Position = lightSpaceMatrix * model * vec4(position, 1.0);
}
