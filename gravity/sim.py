import os
import numpy as np
from pyrr import Vector3
from OpenGL.GL import *
from OpenGL.GL import shaders
from .profiler import PROFILER
from . import util
from .gl_util import *


class NBodySimulation(object):

    num_galaxies = 200 # number of galaxies to generate
    max_particles = num_galaxies # total starting particles
    collision_overlap = 0.25 # max overlap allowed between particles before they collide
    gravity_constant = 100.0
    starting_area_radius = 100.0 # maximum distance from origin galaxies can spawn
    center_star_mass = 1.0e1 # mass of center star of galaxies
    center_star_radius = 3.0 # radius of center star of galaxies

    def __init__(self):
        print('Compiling compute shader')
        with open(os.path.join(os.path.dirname(__file__), 'particle.comp'), 'r') as f:
            shader = shaders.compileShader(f.read(), GL_COMPUTE_SHADER)
        self.shader = shaders.compileProgram(shader)
        glUseProgram(self.shader)

        # assign uniform constant
        glUniform1f(glGetUniformLocation(self.shader, 'gravity_constant'), self.gravity_constant)
        # save variable uniform locations
        self.num_particles_loc = glGetUniformLocation(self.shader, 'num_particles')
        self.dt_loc = glGetUniformLocation(self.shader, 'dt')

        print('Creating compute buffer')
        # create persistant memory-mapped buffer to share memory with GPU and allow fast transfer
        self.particles_ssbo = MappedBufferObject(
            target=GL_SHADER_STORAGE_BUFFER,
            dtype=np.dtype([
                ('position', np.float32, 3),
                ('mass', np.float32, 1),
                ('velocity', np.float32, 3),
                ('radius', np.float32, 1)]),
            length=self.max_particles,
            flags=GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT)
        print('Compute buffer size: {:,d} bytes'.format(self.particles_ssbo.data.nbytes))

        self.num_particles = len(self.particles_ssbo.data)

        galaxy_positions = np.empty((self.num_galaxies, 3), dtype=np.float)
        for pos in galaxy_positions:
            pos[:] = util.rand_spherical(self.starting_area_radius)
        galaxy_positions = iter(galaxy_positions)

        # generate particles
        particles = iter(self.particles_ssbo.data)
        for _ in range(self.num_galaxies):
            center_star = next(particles)
            center_star['position'] = next(galaxy_positions)
            center_star['mass'] = self.center_star_mass
            center_star['velocity'] = 0.0
            center_star['radius'] = self.center_star_radius

        glUseProgram(0)

    def update(self, dt):
        """
        Updates a single frame of the simulation.

        Arguments:
            dt: float in (0, inf), time in seconds since last update
        """
        PROFILER.begin('update')

        glUseProgram(self.shader)

        PROFILER.begin('update.uniforms')
        # update variable uniforms, number of particles and timestep
        glUniform1ui(self.num_particles_loc, self.num_particles)
        glUniform1f(self.dt_loc, dt)

        PROFILER.begin('update.shader')
        # bind particle data buffer to shader buffer 0
        glBindBufferBase(self.particles_ssbo.target, 0, self.particles_ssbo._buf_id)
        # compute shader will calculate gravity forces and update particle data
        glDispatchCompute(self.max_particles, 1, 1)
        # glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
        # glMemoryBarrier(GL_BUFFER_UPDATE_BARRIER_BIT)

        glUseProgram(0)

        # wait for compute shader to finish
        gl_sync()

        PROFILER.end('update')