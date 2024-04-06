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
from PyQt5.QtWidgets import QColorDialog

class GuiFunctions:
    use_distance = False
    distance = None

    def on_voxel_size_change(self):
        value = self.voxel_size_slider.value()
        self.settings.voxel_size_slider_value = value
        print("voxel size: " + str(self.settings.voxel_size_slider_value))


        self._apply_settings()
        self._transform_object()


    def _change_model_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # pv.global_theme.font.color = color.name()
            self.colorTextActually.setStyleSheet(f'background: {color.name()}')
            self.plotter.set_color_cycler([color.name()])
            self.settings.object_color = color.name()

            if self.create_mesh is not None:
                self.plotter.clear()
                self.plotter.add_mesh(self.create_mesh, show_edges=True)



    def _change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            pv.global_theme.font.color = color.name()
            self.colorText.setStyleSheet(f'background: {color.name()}')







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


    def _distance_select(self):


        if self.checkDistance.isChecked():
            def callback(a, b, distance):
                self.label = self.plotter.add_text(f'Distance: {distance*100:.2f}', name='dist')
                self.use_distance = True
            if self.distance is None:
                self.distance = self.plotter.add_measurement_widget(callback)

            self.plotter.update()
        else:
            if self.use_distance:
                self.distance.Off()
                self.distance = None
                self.plotter.remove_actor(self.label)
                self.plotter.update()

    def _show_All_Bounds(self):
        if self.showAllBoundsCheck.isChecked():
            self.test3 = self.plotter.show_bounds(axes_ranges=[0, 100, 0, 100, 0, 100])
            self.plotter.update()


        else:
            print('Checkbox is not checked')
            self.plotter.remove_actor(self.test3)


    def _change_background(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.backgroundActually.setStyleSheet(f'background: {color.name()}')
            self.plotter.set_background(color.name())
            self.settings.background_plotter = color.name()





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

                self.cloud = self.cloud.rotate_x(rotation_x, inplace=True, point=self.cloud.center)
                self.cloud = self.cloud.rotate_y(rotation_y, inplace=True, point=self.cloud.center)
                self.cloud = self.cloud.rotate_z(rotation_z, inplace=True, point=self.cloud.center)

                self.cloud.points *= scale_value



                self.plotter.add_points(self.cloud)
            except Exception as e:
                print("[WARNING] Failed to transform cloud", e)