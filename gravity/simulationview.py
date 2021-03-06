import os
import time

import numpy as np
from pyrr import Vector3, Matrix44

import OpenGL
OpenGL.ERROR_CHECKING = True
OpenGL.FULL_LOGGING = True
from OpenGL.GL import *
from OpenGL.GL import shaders


from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout

from .sim import NBodySimulation
from . import util
from .gl_util import *


class SimulationView(QOpenGLWidget):
    fps = 60
    profiler_print_interval = 1.0

    xcor = 0
    ycor = 0

    def __init__(self, parent):
        super().__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        # focus widget for keyboard controls
        self.setFocus(True)

        self.size = QSize(800, 500)

        self.camera = OrbitCamera(
            distance=100.0,
            azimuth=0.0,
            zenith=np.pi / 2,
            fovx=np.deg2rad(90.0),
            aspect=self.size.width() / self.size.height(),
            near=0.01,
            far=1000.0)

    def sizeHint(self):
        """Overwriting QWidget.sizeHint"""
        return self.size

    def initializeGL(self):

        print_gl_version()
        print('Staring sim')
        self.sim = NBodySimulation()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBlendEquation(GL_FUNC_ADD)

        with open(os.path.join(os.path.dirname(__file__), 'particle.vert'), 'r') as f:
            vshader = shaders.compileShader(f.read(), GL_VERTEX_SHADER)
        with open(os.path.join(os.path.dirname(__file__), 'particle.frag'), 'r') as f:
            fshader = shaders.compileShader(f.read(), GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vshader, fshader)
        glUseProgram(self.shader)

        self.view_loc = glGetUniformLocation(self.shader, 'view')
        self.proj_loc = glGetUniformLocation(self.shader, 'proj')

        # self.object_Color = glGetUniformLocation(self.shader, 'objectColor')
        # self.light_Color = glGetUniformLocation(self.shader, 'lightColor')

        # self.objectColor = (1.0,0.5,0.31);
        # self.light_Color = (1.0,1.0,1.0);

        glUniform1f(glGetUniformLocation(self.shader, 'collision_overlap'), self.sim.collision_overlap)
        glUniform1ui(glGetUniformLocation(self.shader, 'color_mode'), 1)

        self.particles_vao = glGenVertexArrays(1)
        glBindVertexArray(self.particles_vao)

        # VBO of sprite verticies (the same for each sprite)
        self.sprite_data_vbo = ConstBufferObject(
            usage=GL_STATIC_DRAW,
            target=GL_ARRAY_BUFFER,
            data=np.array(
                [([-1.0,  1.0], [0.0, 1.0]),
                 ([-1.0, -1.0], [0.0, 0.0]),
                 ([ 1.0,  1.0], [1.0, 1.0]),
                 ([ 1.0, -1.0], [1.0, 0.0])],
                dtype=np.dtype([
                    ('vertex', np.float32, 2),
                    ('uv', np.float32, 2)])))
        # bind shader attributes for sprite verticies
        setup_vbo_attrs(
            vbo=self.sprite_data_vbo,
            shader=self.shader,
            attr_prefix='sprite_')


        # bind shader attributes for particle data
        setup_vbo_attrs(
            vbo=self.sim.particles_ssbo,
            shader=self.shader,
            attr_prefix='particle_',
            divisor=1)

        glBindVertexArray(0)
        glUseProgram(0)

        print('Starting animation timer')
        # interval-> (1000/FPS) milliseconds
        self.last_update_time = time.time() - 1 / self.fps
        self.ani_timer = QTimer(self)
        self.ani_timer.setInterval(1000 / self.fps)
        self.ani_timer.timeout.connect(self.update)
        self.ani_timer.start()

        self.last_profiler_print_time = time.time()

        self.paused = True

        print('initializing successful')

    def update(self):
        """Updates one frame of animation."""
        t = time.time()
        dt = t - self.last_update_time
        self.last_update_time = t

        if not self.paused:
            self.sim.update(dt)

        super().update()


    def paintGL(self):
        """Overwriting QOpenGLWidget.paintGL ( Called when OpenGL is ready to paint a frame)"""

        # clear to black
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self.shader)
        glBindVertexArray(self.particles_vao)

        #-------------------------camera------------------------
        self.camera.update()
        glUniformMatrix4fv(self.view_loc, 1, GL_TRUE, self.camera.view.astype(np.float32))
        glUniformMatrix4fv(self.proj_loc, 1, GL_TRUE, self.camera.proj.astype(np.float32))

        p = self.sim.particles_ssbo.data

        p[:] = p[np.argsort(-np.sum(np.square(p[:]['position'] - self.camera.eye), axis=1))]

        glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, self.sprite_data_vbo.length, self.sim.num_particles)
        gl_sync()
        glBindVertexArray(0)
        glUseProgram(0)



    def resizeGL(self, width, height):
        """
        Overrides QOpenGLWidget.resizeGL
        Called when the OpenGL surface is resized with the new size
        """
        # just save the new size and recalculate the camera aspect
        self.size = QSize(width, height)
        self.camera.aspect = self.size.width() / self.size.height()

    def mousePressEvent(self, event):
        """
        Overrides QWidget.mousePressEvent
        Called when the user presses a mouse button on the widget.
        """
        if event.buttons() == Qt.LeftButton:
            # save drag starting mouse position and camera position
            self.drag_mouse_start = event.pos()
            self.drag_cam_start = (self.camera.azimuth, self.camera.zenith)




    def mouseMoveEvent(self, event):
        """
        Overrides QWidget.mouseMoveEvent
        Called when the user moves the mouse over the widget or when dragging the mouse from the widget.
        """
        if event.buttons() & Qt.LeftButton == Qt.LeftButton:
            # difference vector from drag start
            drag = event.pos() - self.drag_mouse_start
            # convert to NumPy array
            drag = np.array([drag.x(), -drag.y()], dtype=np.float)
            # scale drag to 180 degrees every 500 pixels
            drag = util.lerp(drag, 0, 500, 0, np.pi)
            # add to starting camera angles
            azimuth, zenith = self.drag_cam_start
            azimuth += drag[0]
            zenith += drag[1]
            # set camera angles
            self.camera.azimuth = azimuth
            self.camera.zenith = zenith

    def wheelEvent(self, event):
        """
        Overrides QWidget.wheelEvent
        Called when the user scrolls the mouse wheel on the widget.
        """
        # get scroll amount
        scroll = event.angleDelta().y()
        # scale to 0.25 zoom every 120 points
        zoom = util.lerp(-scroll, 0, 120, 0, 0.25)
        # scale camera distance and clipping planes exponentially by zoom
        self.camera.distance = 2 ** (np.log2(self.camera.distance) + zoom)
        self.camera.near = 2 ** (np.log2(self.camera.near) + zoom)
        self.camera.far = 2 ** (np.log2(self.camera.far) + zoom)

    def keyPressEvent(self, event):
        """
        Overrides QWidget.keyPressEvent
        Called when the user presses a key on the widget.
        """
        if event.key() == Qt.Key_Space:
            # toggle pause
            self.paused = not self.paused

class Camera(object):
    """
    Class representing a 3D camera.
    """

    def __init__(self, eye, at, up, fovx, aspect, near, far):
        """
        Creates a new camera.

        Arguments:
            eye: Vector3, the eye position of the camera
            at: Vector3, the point the camera is looking towards
            up: Vector3, the up-vector of the camera indicating its orientation, should not be parallel with eye - at
            fovx: float in (0, pi), the FOV angle in radians in the x-direction
            aspect: float in (0, inf), the aspect ratio of the viewing portal
            near: float in [0, far), the distance of the near clipping plane to the camera
            far: float in (near, inf), the distance of the far clipping plane to the camera
        """
        self.eye = eye
        self.at = at
        self.up = up
        self.fovx = fovx
        self.aspect = aspect
        self.near = near
        self.far = far

        self.update()

    def update(self):
        """
        Updates the camera's view matricies to match the camera's settings.
        """
        eye = self.eye
        at = self.at
        up = self.up

        # orthonormalization of camera axes
        n = (eye - at).normalised
        u = up.cross(n).normalised
        v = n.cross(u)
        # camera view matrix
        self.view = Matrix44(
            [[u.x, u.y, u.z, -u.dot(eye)],
             [v.x, v.y, v.z, -v.dot(eye)],
             [n.x, n.y, n.z, -n.dot(eye)],
             [  0,   0,   0,           1]])

        fovx = self.fovx
        aspect = self.aspect
        near = self.near
        far = self.far

        # symmetrical perspective projection matrix
        recip_tan_fov = 1 / np.tan(fovx / 2)
        a = recip_tan_fov
        b = aspect * recip_tan_fov
        c = -(far + near) / (far - near)
        d = -2 * far * near / (far - near)
        self.proj = Matrix44(
            [[a, 0,  0, 0],
             [0, b,  0, 0],
             [0, 0,  c, d],
             [0, 0, -1, 0]])

class OrbitCamera(Camera):
    """
    Class representing a camera that points towards the origin and
    can easily be controlled to orbit around the origin.
    """

    # epsilon to prevent camera from going fully vertical, which would cause loss of rotational control
    zenith_eps = 1e-5 * np.pi

    def __init__(self, distance, azimuth, zenith, fovx, aspect, near, far):
        """
        Creates a new orbiting camera.

        Arguments:
            distance: float in (0, inf), the desired distance from the center to the camera
            azimuth: float in [0, 2pi], the angle in radians to orbit around the vertical
            zenith: float in [-pi, pi], the angle in radians from the ground plane
            fovx: float in (0, pi), the FOV angle in radians in the x-direction
            aspect: float in (0, inf), the aspect ratio of the viewing portal
            near: float in [0, far), the distance of the near clipping plane to the camera
            far: float in (near, inf), the distance of the far clipping plane to the camera
        """
        self.distance = distance
        self.azimuth = azimuth
        self.zenith = zenith
        super().__init__(
            eye=Vector3(),
            at=Vector3(),
            up=Vector3([0.0, 1.0, 0.0]),
            fovx=fovx,
            aspect=aspect,
            near=near,
            far=far)

    def update(self):
        self.azimuth %= np.pi * 2
        self.zenith = np.clip(self.zenith, self.zenith_eps, np.pi - self.zenith_eps)
        eye = util.from_spherical(self.distance, self.azimuth, self.zenith)
        self.eye = Vector3([eye.x, eye.z, eye.y])
        super().update()
