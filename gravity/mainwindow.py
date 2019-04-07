from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QLabel
from .simulationview import SimulationView
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Particle Gravity Simulator')

        self.sim_view = SimulationView(self)
        self.setCentralWidget(self.sim_view)

        layout_box = QHBoxLayout(self.sim_view)
        layout_box.setContentsMargins(0, 0, 0, 0)

        l1 = QLabel(self.sim_view)
        l1.setText("<font color='red'> Space: Pause/Play | Mouse:Move Camera | Scroll: Zoom \n</font>")
        l1.setAlignment(Qt.AlignLeft)
        l1.adjustSize()
		