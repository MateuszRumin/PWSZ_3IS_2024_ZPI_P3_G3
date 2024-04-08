import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import open3d as o3d
import laspy
import numpy as np
import pyvista as pv
from pyntcloud import PyntCloud


class ApplySettings:
    def _apply_settings(self):
        self.scale_value_label.setText(str(self.settings.scale_value))

        self.create_mesh_button.setEnabled(self.settings.enable_buttons_cloud)

        #Enable export buttons
        self.export_to_ply.setEnabled(self.settings.enable_buttons_cloud)
        self.export_to_pcd.setEnabled(self.settings.enable_buttons_cloud)
        self.export_to_obj.setEnabled(self.settings.enable_buttons_mesh)
        self.export_to_stl.setEnabled(self.settings.enable_buttons_mesh)

        pv.global_theme.font.color = self.settings.font_color_plotter
        self.plotter.set_background(self.settings.background_plotter)
        self.plotter.set_color_cycler([self.settings.object_color])
        self.colorTextActually.setStyleSheet(f'background: {self.settings.object_color}')
        self.colorText.setStyleSheet(f'background: {self.settings.colorTextPlot}')

        self.display_cloud_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_normals_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_mesh_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        self.display_triangles_checkbox.setEnabled(self.settings.enable_buttons_mesh)


        self.triangles_amount_input_field.setText(str(self.settings.triangles_amount))

