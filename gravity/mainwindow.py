from PyQt5.QtWidgets import QMainWindow
from .simulationview import SimulationView
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Particle Gravity Simulator')

        self.layout = QVBoxLayout()
        self.label = QLabel("Hello There")

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


        self.sim_view = SimulationView(self)
        self.setCentralWidget(self.sim_view)