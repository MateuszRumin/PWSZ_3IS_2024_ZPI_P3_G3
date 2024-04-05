import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import open3d as o3d
import laspy
import numpy as np
import pyvista as pv
from pyntcloud import PyntCloud


class Settings:
    def __init__(self):
        self.file_path = None
        self.voxel_size_slider_value = 1
        self.scale_value = 1
        self.object_move_in_x_direction = 0
        self.object_move_in_y_direction = 0
        self.object_move_in_z_direction = 0
        self.rotate_slider_x_value = 0
        self.rotate_slider_y_value = 0
        self.rotate_slider_z_value = 0
        self.enable_buttons_cloud = False
        self.enable_buttons_mesh = False


        self.font_color_plotter = 'white'
        self.background_plotter = 'white'

