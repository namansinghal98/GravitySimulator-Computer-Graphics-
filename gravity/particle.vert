#version 450 core

uniform mat4 view;         // camera view matrix
uniform mat4 proj;        // camera projection matrix

in vec2 sprite_vertex;
in vec2 sprite_uv;                                                    
in float particle_radius;
in float particle_mass;
in vec3 particle_position;
in vec3 particle_velocity;



out vec2 frag_uv;
out vec3 WorldPos;
out vec3 Normal;



void main() {

	WorldPos = particle_position;
    frag_uv = sprite_uv;
    Normal = vec3(sprite_vertex,0.0);

    vec3 cam_right = vec3(view[0][0], view[1][0], view[2][0]);                  //cam right vector
    vec3 cam_up    = vec3(view[0][1], view[1][1], view[2][1]);                  //cam up vector

    vec3 vert = (sprite_vertex.x * cam_right + sprite_vertex.y * cam_up);       //vertices only in camera space
    vert *= particle_radius * 1.0;


    gl_Position = proj * view * vec4(vert + particle_position, 1.0);  //into view space
}
