import math
import copy
import threading
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import open3d as o3d
import laspy
import pyvista as pv
from pyntcloud import PyntCloud


class GuiFunctions:


    def on_voxel_size_change(self):
        value = self.voxel_size_slider.value()
        self.settings.voxel_size_slider_value = value
        print("voxel size: " + str(self.settings.voxel_size_slider_value))


        self._apply_settings()
        self._transform_object()

    def _change_scale(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.scale_value = round((self.settings.scale_value + 0.1), 1)

            elif key == "-":
                if self.settings.scale_value > 0.1:
                    self.settings.scale_value = round((self.settings.scale_value - 0.1), 1)
            print(self.settings.scale_value)
            self._apply_settings()
            self._transform_object()



    def move_in_x_axis(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.object_move_in_x_direction += 0.005
            elif key == "-":
                self.settings.object_move_in_x_direction -= 0.005
            self._transform_object()


    def move_in_y_axis(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.object_move_in_y_direction += 0.005
            elif key == "-":
                self.settings.object_move_in_y_direction -= 0.005
            self._transform_object()


    def move_in_z_axis(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.object_move_in_z_direction += 0.005
            elif key == "-":
                self.settings.object_move_in_z_direction -= 0.005
            self._transform_object()


    def _rotation_slider_x_change(self):
        if self.cloud is not None:
            value = self.rotation_x_slider.value()
            self.settings.rotate_slider_x_value = int(value)
            self._transform_object()

    def _rotation_slider_y_change(self):
        if self.cloud is not None:
            value = self.rotation_y_slider.value()
            self.settings.rotate_slider_y_value = int(value)
            self._transform_object()

    def _rotation_slider_z_change(self):
        if self.cloud is not None:
            value = self.rotation_z_slider.value()
            self.settings.rotate_slider_z_value = int(value)
            self._transform_object()

    def _transform_object(self):
        if self.cloud is not None:
            try:
                self.cloud = copy.deepcopy(self.cloud_backup)

                self.plotter.clear()

                #read value from gui
                move_x = self.settings.object_move_in_x_direction
                move_y = self.settings.object_move_in_y_direction
                move_z = self.settings.object_move_in_z_direction

                rotation_x = self.settings.rotate_slider_x_value
                rotation_y = self.settings.rotate_slider_y_value
                rotation_z = self.settings.rotate_slider_z_value

                scale_value = self.settings.scale_value

                voxel_size = self.settings.voxel_size_slider_value / 10000

                #-------

                translation_vector = np.array([move_x, move_y, move_z])
                self.cloud.points += translation_vector

                self.cloud = self.cloud.rotate_x(rotation_x)
                self.cloud = self.cloud.rotate_y(rotation_y)
                self.cloud = self.cloud.rotate_z(rotation_z)

                self.cloud.points *= scale_value



                self.plotter.add_points(self.cloud)
            except Exception as e:
                print("[WARNING] Failed to transform cloud", e)