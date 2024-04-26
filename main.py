import sys

# Setting the Qt bindings for QtPy
import os
os.environ["QT_API"] = "pyqt5"

from qtpy import QtWidgets

import numpy as np

import pyvista as pv
from pyvistaqt import QtInteractor, MainWindow

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import QLocale

import psutil
import time
import signal

import threading

from settings import  Settings
from functions import file_functions
from functions import apply_settings
from functions import gui_functions
from functions import mesh_creator
from functions import cloud_selection
from functions import mesh_selection
from normalization import normalization


class MyMainWindow(MainWindow, file_functions.FileFunctions, apply_settings.ApplySettings, gui_functions.GuiFunctions, mesh_creator.MeshCreator, cloud_selection.CloudSelection, mesh_selection.MeshSelection, normalization.NormalizationClass):

    def __init__(self, parent=None, show=True):
        QtWidgets.QMainWindow.__init__(self, parent)
        uic.loadUi("UI2.ui", self)
        self.settings = Settings()


        # plotter plain
        self.plotter_frame = QtWidgets.QFrame()
        self.plotter = QtInteractor(self.plotter_frame)
        self.vlayout.addWidget(self.plotter.interactor)
        self.plotter_frame.setLayout(self.vlayout)
        self.plotter.camera.SetFocalPoint(0, 0, 0)
        self.plotter.camera.SetViewUp(0, 0, 0)
        self.plotter.add_axes()


        # Setting toolbox to scene geometries
        self.toolBox.setCurrentIndex(0)

        # Loading parameters from the settings
        self._apply_settings()

        # -------------------Version 1.20-------------------------------
        # -------------------Adding triggers-----------------------------

        # -------------------Action Bar--------------------------------#
        self.actionOpen.triggered.connect(self.open_file)
        self.actionRead_cloud_from_mesh.triggered.connect(self.read_cloud_from_mesh)

        # -------------------Scene geometries--------------------------#
        self.display_cloud_checkbox.clicked.connect(self._show_cloud_checked)
        self.display_normals_checkbox.clicked.connect(self._show_normals_checked)
        self.display_mesh_checkbox.clicked.connect(self._show_mesh_checked)
        self.display_triangles_checkbox.clicked.connect(self._show_triangles_checked)
        #Reset layout
        self.reset_layout_button.clicked.connect(self._reset_plotter)

        # -------------------Complements-------------------------------#
        # Background Color
        self.changeBackground.clicked.connect(self._change_background)
        # Model Color
        self.modelColor.clicked.connect(self._change_model_color)
        # Text Color
        self.textColorbtn.clicked.connect(self._change_text_color)
        # Calculate
        self.calculate_area_button.clicked.connect(self._calculate_area)
        # Show All Bounds
        self.showAllBoundsCheck.clicked.connect(self._show_All_Bounds)
        # Distance
        self.checkDistance.clicked.connect(self._distance_select)


        # -------------------Geometry transformation-------------------#
        # Down sampling
        self.voxel_size_slider.valueChanged.connect(self.on_downSampling_size_change)
        # Scale
        self.scale_up_button.clicked.connect(lambda: self._change_scale("+"))
        self.scale_down_button.clicked.connect(lambda: self._change_scale("-"))
        #Displacements
        self.validator = QDoubleValidator()
        locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.validator.setLocale(locale)    #Allowing to enter dots as a separator
        #--
        self.move_x_value_field.setValidator(self.validator)
        self.move_y_value_field.setValidator(self.validator)
        self.move_z_value_field.setValidator(self.validator)
        #--
        self.move_x_value_field.textChanged.connect(self.move_in_x_axis)
        self.move_y_value_field.textChanged.connect(self.move_in_y_axis)
        self.move_z_value_field.textChanged.connect(self.move_in_z_axis)
        #--
        # Rotate x
        self.rotation_x_slider.valueChanged.connect(self._rotation_slider_x_change)
        # Rotate y
        self.rotation_y_slider.valueChanged.connect(self._rotation_slider_y_change)
        # Rotate z
        self.rotation_z_slider.valueChanged.connect(self._rotation_slider_z_change)
        #Apply values
        self.apply_transformation_values_button.clicked.connect(self._transform_object)

        # -------------------Selections--------------------------------#
        # Select Points
        self.select_points_button.clicked.connect(self._select_points)
        # Select Single point
        self.delete_points_button.clicked.connect(self._select_single_point)
        # Delete Selected Points
        self.delete_selected_points_button.clicked.connect(self._delete_selected_points)
        # Extract selected points
        self.extract_selected_points_button.clicked.connect(self._extract_selected_points)

        # -------------------Convert to mesh---------------------------#
        # Create mesh
        self.create_mesh_button.clicked.connect(self._make_mesh)
        # Fix mesh
        self.fix_mesh_button.clicked.connect(self.repair_mesh)
        # Reduce triangles
        self.reduce_triangles_button.clicked.connect(self.transform_existing_mesh)
        # Triangles amount
        self.triangles_amount_input_field.setValidator(QIntValidator(1, 100, self))
        self.triangles_amount_input_field.textChanged.connect(self._triangles_amount_changed)
        self.triangles_amount_checkbox.clicked.connect(self._enable_triangles_amount_input_field)
        # Smooth button
        self.smooth_button.clicked.connect(self._smooth_mesh)

        self.takephoto.clicked.connect(self._take_screen)


        # Subdevide button
        self.subdevideBtn.clicked.connect(self._subdevide_triangles)
        self.iterationSubdevide.textChanged.connect(self._on_number_of_subdevided_value_changed)
        #Cross selection
        self.cross_selection_checkbox.clicked.connect(self._reset_plotter)
        # Number of iterations for smooth field
        self.smooth_number_of_iterations_field.setValidator(QIntValidator(1, 10000, self))
        self.smooth_number_of_iterations_field.textChanged.connect(self._on_number_of_smooth_operations_value_changed)
        # Edit mesh
        self.edit_meshBtn.clicked.connect(self._edit_mesh)
        # Crop mesh
        self.cropMeshButton.clicked.connect(self.crop_mesh_box)
        # Select area
        self.select_mesh_area_button.clicked.connect(self.select_mesh_area)
        # Crop selection mesh
        self.cropMeshSelected.clicked.connect(self.crop_mesh_selected)
        # Extract mesh
        self.extractMesh.clicked.connect(self.extract_mesh)


        # -------------------Normalization----------------------------#
        # Normalize checkbox
        self.normalize_checkbox.clicked.connect(self.normalize_checkbox_changed)
        #Normalize preset
        self.normalization_preset_combobox.currentTextChanged.connect(self._normalize_preset_changed)
        #Change values manually
        self.change_values_manually_checkbox.clicked.connect(self._change_values_manually_checkbox_changed)
        # Model iterations
        self.model_iterations_slider.valueChanged.connect(self._model_iterations_slider_change)
        # Prop iterations
        self.prop_iterations_slider.valueChanged.connect(self._prop_iteration_slider_changed)
        # Number of parts
        self.number_of_parts_slider.valueChanged.connect(self._number_of_parts_slider_changed)
        # Minimum points on path
        self.min_points_on_path_slider.valueChanged.connect(self._min_points_on_path_slider_changed)
        # Curvature threshold
        self.curvature_treshold_slider.valueChanged.connect(self.curvature_threshold_slider_changed)
        #Neighbours
        self.neighbours_slider.valueChanged.connect(self.neighbours_slider_changed)




        # -------------------Exports-----------------------------------#
        # OBJ
        self.export_to_obj.clicked.connect(lambda: self._on_export_to_obj(self.create_mesh))
        # STL
        self.export_to_stl.clicked.connect(lambda: self._on_export_to_stl(self.create_mesh))
        # PLY
        self.export_to_ply.clicked.connect(self._on_export_to_ply)
        # Mesh to PLY
        self.export_mesh_to_ply.clicked.connect(self._on_export_mesh_to_ply)

        # -------------------------------------------------------------#

        # Ram monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_memory_usage)
        monitor_thread.daemon = True
        monitor_thread.start()

        if show:
            self.show()


    def monitor_memory_usage(self):
        #Obtaining RAM information from the system
        process = psutil.Process()
        mem_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()
        #-----------------------------------------

        total_memory = virtual_memory.total / (1024 * 1024 * 1024)  #Calculating total system memory
        while True:
            #RAM status bar
            virtual_memory = psutil.virtual_memory()
            used_ram = round((virtual_memory.used / (1024 * 1024 * 1024)), 2)
            ram_usage = round(((used_ram * 100) / (total_memory - 0.5)), 0)
            self.memoryBar.setValue(int(ram_usage))
            #---------------------------------------

            #If the free RAM drops below 500 MB, the application turns off
            if round((virtual_memory.available / (1024 * 1024)), 0) < 500:
                print("Insufficient free RAM")
                os.kill(os.getpid(), signal.SIGTERM)
            #-------------------------------------------------------------
            time.sleep(1)   #The condition is checked every second


    #Key function for resetting plotter called from file functions.
    # Do not use directly!
    # You should use the function located in file_functions!
    # Do not delete!
    def reload_plotter(self):
        try:
            # Deleting existing plotter
            if hasattr(self, 'plotter_frame'):
                self.plotter_frame.deleteLater()

            # Creating new plotter
            self.plotter_frame = QtWidgets.QFrame()
            self.plotter = QtInteractor(self.plotter_frame)
            self.vlayout.addWidget(self.plotter.interactor)
            self.plotter_frame.setLayout(self.vlayout)
            self.plotter.camera.SetFocalPoint(0, 0, 0)
            self.plotter.camera.SetViewUp(0, 0, 0)
            self.plotter.add_axes()

            self._apply_settings()
        except Exception as e:
            print("[WARNING] Failed to reload plotter", e)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())