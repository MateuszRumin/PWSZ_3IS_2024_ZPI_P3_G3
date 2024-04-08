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
        self.file_path = None                       #Path to file
        self.downSampling_size_slider_value = 1     #DownSampling value
        self.scale_value = 1                        #Scale factor
        self.triangles_amount = 1000                #Triangles amount

        #Cloud move values
        self.object_move_in_x_direction = 0
        self.object_move_in_y_direction = 0
        self.object_move_in_z_direction = 0

        #Cloud rotation values
        self.rotate_slider_x_value = 0
        self.rotate_slider_y_value = 0
        self.rotate_slider_z_value = 0

        #Export buttons
        self.enable_buttons_cloud = False
        self.enable_buttons_mesh = False
        self.normals_computed_for_origin = False
        self.changed_normals_computed = False

        #Colors
        self.font_color_plotter = 'lightblue'
        self.background_plotter = 'gray'
        self.object_color = 'white'
        self.colorTextPlot = 'white'

