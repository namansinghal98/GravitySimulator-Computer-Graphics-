import os
import numpy as np
from pyrr import Vector3
from OpenGL.GL import *
from OpenGL.GL import shaders
from . import util
from .gl_util import *


class NBodySimulation(object):

    num_particles = 3
    collision_overlap = 0.25 # Currently not used
    gravity_constant = 100.0
    particle_mass = 1.0e1 
    particle_radius = 5.0 
    filename = 'input.txt'

    def __init__(self):

        print('Compiling compute shader')
        with open(os.path.join(os.path.dirname(__file__), 'particle.comp'), 'r') as f:
            shader = shaders.compileShader(f.read(), GL_COMPUTE_SHADER)
        self.shader = shaders.compileProgram(shader)
        glUseProgram(self.shader)

        glUniform1f(glGetUniformLocation(self.shader, 'gravity_constant'), self.gravity_constant)
        self.num_particles_loc = glGetUniformLocation(self.shader, 'num_particles')
        self.dt_loc = glGetUniformLocation(self.shader, 'dt')

        input_file = open(self.filename,"r") 
        s1 = input_file.readline()
        self.num_particles = int(s1)

        print('Creating compute buffer')
        self.particles_ssbo = MappedBufferObject(
            target=GL_SHADER_STORAGE_BUFFER,
            dtype=np.dtype([
                ('position', np.float32, 3),
                ('mass', np.float32, 1),
                ('velocity', np.float32, 3),
                ('radius', np.float32, 1)]),
            length=self.num_particles,
            flags=GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT)
        print('Compute buffer size: {:,d} bytes'.format(self.particles_ssbo.data.nbytes))

        galaxy_positions = np.empty((self.num_particles, 3), dtype=np.float)
        galaxy_velocities = np.empty((self.num_particles, 3), dtype=np.float)

        def is_float(n):
            try:
                float(n)
                return True
            except:
                return False

        for pos in galaxy_positions:
            s1 = input_file.readline()
            y = [float(n) for n in s1.split(' ') if is_float(n)]
            pos[:] = y[:]

        for vel in galaxy_velocities:
            s1 = input_file.readline()
            y = [float(n) for n in s1.split(' ') if is_float(n)]
            vel[:] = y[:]
            
            
        galaxy_positions = iter(galaxy_positions)
        galaxy_velocities = iter(galaxy_velocities)

        particles = iter(self.particles_ssbo.data)
        for _ in range(self.num_particles):
            center_star = next(particles)
            center_star['position'] = next(galaxy_positions)
            center_star['mass'] = self.particle_mass
            center_star['velocity'] = next(galaxy_velocities)
            center_star['radius'] = self.particle_radius

        glUseProgram(0)

    def update(self, dt):
        """Updates a single frame of the simulation (dt: float in (0, inf), time in seconds since last update)"""
        glUseProgram(self.shader)
        glUniform1ui(self.num_particles_loc, self.num_particles)
        glUniform1f(self.dt_loc, dt)
        glBindBufferBase(self.particles_ssbo.target, 0, self.particles_ssbo._buf_id)
        glDispatchCompute(self.num_particles, 1, 1)
        glUseProgram(0)
        gl_sync()
