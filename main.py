import PyQt5.QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore, QtGui, QtWidgets

import sys
import os

from pyvistaqt import QtInteractor
import numpy as np
import pyvista as pv

from pyvista import examples

import open3d as o3d
import laspy

from settings import  Settings
from functions import file_functions
from functions import apply_settings
from functions import gui_functions
from functions import mesh_creator
from functions import cloud_selection



class MyGUI(QMainWindow, file_functions.FileFunctions, apply_settings.ApplySettings, gui_functions.GuiFunctions, mesh_creator.MeshCreator, cloud_selection.CloudSelection):

    def __init__(self):
        self.settings = Settings()
        super(MyGUI, self).__init__()
        uic.loadUi("UI2.ui", self)
        self.show()

        #plotter plain
        self.plotter_frame = QtWidgets.QFrame()
        self.plotter = QtInteractor(self.plotter_frame)
        self.vlayout.addWidget(self.plotter.interactor)
        self.plotter_frame.setLayout(self.vlayout)
        self.plotter.camera.SetFocalPoint(0, 0, 0)
        self.plotter.camera.SetViewUp(0, 0, 0)
        self.plotter.show_axes_all()


        self._apply_settings()


        #--------------------------------------------------
        #Adding trigers
        self.actionOpen.triggered.connect(self.open_file)

        self.voxel_size_slider.valueChanged.connect(self.on_voxel_size_change)

        self.scale_up_button.clicked.connect(lambda: self._change_scale("+"))
        self.scale_down_button.clicked.connect(lambda: self._change_scale("-"))

        self.move_x_up_button.clicked.connect(lambda: self.move_in_x_axis("+"))
        self.move_x_down_button.clicked.connect(lambda: self.move_in_x_axis("-"))

        self.move_y_up_button.clicked.connect(lambda: self.move_in_y_axis("+"))
        self.move_y_down_button.clicked.connect(lambda: self.move_in_y_axis("-"))

        self.move_z_up_button.clicked.connect(lambda: self.move_in_z_axis("+"))
        self.move_z_down_button.clicked.connect(lambda: self.move_in_z_axis("-"))

        self.rotation_x_slider.valueChanged.connect(self._rotation_slider_x_change)
        self.rotation_y_slider.valueChanged.connect(self._rotation_slider_y_change)
        self.rotation_z_slider.valueChanged.connect(self._rotation_slider_z_change)

        self.create_mesh_button.clicked.connect(self._make_mesh)

        self.export_to_obj.clicked.connect(lambda: self._on_export_to_obj(self.create_mesh))
        self.export_to_stl.clicked.connect(lambda: self._on_export_to_stl(self.create_mesh))
        self.export_to_ply.clicked.connect(self._on_export_to_ply)
        self.export_to_pcd.clicked.connect(self._on_export_to_pcd)

        self.select_points_button.clicked.connect(self._select_points)
        self.delete_points_button.clicked.connect(self._delete_points)
        self.delete_selected_points_button.clicked.connect(self._delete_selected_points)

def main():
    app = QApplication([])
    window = MyGUI()

    app.exec_()


if __name__ == '__main__':
    main()