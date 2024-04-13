"""
#######################################################################################################################################
||                                                                                                                                   ||
||                                                          Apply Settings                                                           ||
||                                                                                                                                   ||
||                This file is responsible for implementing the values stored in the settings into the application.                  ||
||It is called at the start of the application, and it must be called every time we want to implement a value found in the settings. ||
||                                                                                                                                   ||
#######################################################################################################################################
"""
import sys
import open3d as o3d
import laspy
import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from pyntcloud import PyntCloud


class ApplySettings:
    def _apply_settings(self):
        #---------------Settings of element values---------------------#
        self.scale_value_label.setText(str(self.settings.scale_value))                      #Scale value label
        self.triangles_amount_input_field.setText(str(self.settings.triangles_amount))      #Triangles amount input field
        #--------------------------------------------------------------#

        #---------------------Enable objects---------------------------#
        #Export buttons
        self.export_to_ply.setEnabled(self.settings.enable_buttons_cloud)
        self.export_to_obj.setEnabled(self.settings.enable_buttons_mesh)
        self.export_to_stl.setEnabled(self.settings.enable_buttons_mesh)
        #------------------
        #Create mesh button
        if self.settings.enable_buttons_cloud or self.settings.enable_create_mesh_button:
            self.create_mesh_button.setEnabled(True)
        else:
            self.create_mesh_button.setEnabled(False)
        #------------------
        #Crop mesh button
        self.cropMeshButton.setEnabled(self.settings.enable_buttons_mesh)
        #----------------
        #Change normals button
        self.change_normals_button.setEnabled(self.settings.enable_buttons_cloud)
        #---------------------
        #Save normals button
        self.save_normals_button.setEnabled(self.settings.enable_buttons_cloud)
        #-------------------
        #Fix mesh button
        self.fix_mesh_button.setEnabled(self.settings.enable_buttons_mesh)
        #---------------
        #Enable display checkboxs
        self.display_cloud_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_normals_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_mesh_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        self.display_triangles_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        #------------------
        #Enable all bounds checkbox
        if self.settings.enable_buttons_cloud == True or self.settings.enable_buttons_mesh == True:
            self.showAllBoundsCheck.setEnabled(True)
        #--------------------------
        #Enable triangles input field
        self.triangles_amount_input_field.setEnabled(self.settings.enable_triangles_amount_input_field)
        #--------------------------------------------------------------#

        #-----------------Theme and colors settings---------------------#
        pv.global_theme.font.color = self.settings.font_color_plotter                       #Font color
        self.plotter.set_background(self.settings.background_plotter)                       #Background color
        self.plotter.set_color_cycler([self.settings.object_color])                         #Object color
        self.colorTextActually.setStyleSheet(f'background: {self.settings.object_color}')   #Color text actually
        self.colorText.setStyleSheet(f'background: {self.settings.colorTextPlot}')          #Color text
        #---------------------------------------------------------------#
