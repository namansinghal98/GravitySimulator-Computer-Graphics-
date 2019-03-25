from PyQt5.QtWidgets import QMainWindow
from .simulationview import SimulationView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Particle Gravity Simulator')
        self.sim_view = SimulationView(self)
        self.setCentralWidget(self.sim_view)