"""
################################################################################################
||                                                                                            ||
||                                            Main                                            ||
||                                                                                            ||
||                     Main application file. Contains the gui connection                     ||
||                                                                                            ||
################################################################################################
"""
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import QIntValidator

import os

import psutil
import time
import signal



from pyvistaqt import QtInteractor

import threading


from settings import  Settings
from functions import file_functions
from functions import apply_settings
from functions import gui_functions
from functions import mesh_creator
from functions import cloud_selection
from functions import mesh_selection
from functions import normals_selection
from normalization import normalization


class MyGUI(QMainWindow, file_functions.FileFunctions, apply_settings.ApplySettings, gui_functions.GuiFunctions, mesh_creator.MeshCreator, cloud_selection.CloudSelection, mesh_selection.MeshSelection, normals_selection.NormalsSelection, normalization.NormalizationClass):

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
        self.plotter.renderer.SetUseShadows(True)
        self.plotter.show_axes_all()

        #Setting toolbox to scene geometries
        self.toolBox.setCurrentIndex(0)

        #Loading parameters from the settings
        self._apply_settings()


        #-------------------Version 1.20-------------------------------
        #-------------------Adding trigers-----------------------------

        #-------------------Action Bar--------------------------------#
        self.actionOpen.triggered.connect(self.open_file)

        # -------------------Scene geometries--------------------------#
        self.display_cloud_checkbox.clicked.connect(self._show_cloud_checked)
        self.display_normals_checkbox.clicked.connect(self._show_normals_checked)
        self.display_mesh_checkbox.clicked.connect(self._show_mesh_checked)
        self.display_triangles_checkbox.clicked.connect(self._show_triangles_checked)

        #-------------------Complements-------------------------------#
        #Background Color
        self.changeBackground.clicked.connect(self._change_background)
        #Model Color
        self.modelColor.clicked.connect(self._change_model_color)
        #Text Color
        self.textColorbtn.clicked.connect(self._change_text_color)
        #Downsampling
        self.voxel_size_slider.valueChanged.connect(self.on_downSampling_size_change)
        #Scale
        self.scale_up_button.clicked.connect(lambda: self._change_scale("+"))
        self.scale_down_button.clicked.connect(lambda: self._change_scale("-"))
        #Calculate

        #Show All Bounds
        self.showAllBoundsCheck.clicked.connect(self._show_All_Bounds)
        #Distance
        self.checkDistance.clicked.connect(self._distance_select)

        # -------------------Move object-------------------------------#
        # Move x
        self.move_x_up_button.clicked.connect(lambda: self.move_in_x_axis("+"))
        self.move_x_down_button.clicked.connect(lambda: self.move_in_x_axis("-"))
        # Move y
        self.move_y_up_button.clicked.connect(lambda: self.move_in_y_axis("+"))
        self.move_y_down_button.clicked.connect(lambda: self.move_in_y_axis("-"))
        # Move z
        self.move_z_up_button.clicked.connect(lambda: self.move_in_z_axis("+"))
        self.move_z_down_button.clicked.connect(lambda: self.move_in_z_axis("-"))
        # Rotate x
        self.rotation_x_slider.valueChanged.connect(self._rotation_slider_x_change)
        # Rotate y
        self.rotation_y_slider.valueChanged.connect(self._rotation_slider_y_change)
        # Rotate z
        self.rotation_z_slider.valueChanged.connect(self._rotation_slider_z_change)

        #-------------------Selections--------------------------------#
        #Select Points
        self.select_points_button.clicked.connect(self._select_points)
        #Select Single point
        self.delete_points_button.clicked.connect(self._select_single_point)
        #Delete Selected Points
        self.delete_selected_points_button.clicked.connect(self._delete_selected_points)
        #Edit mesh
        self.edit_meshBtn.clicked.connect(self._edit_mesh)

        #-------------------Convert to mesh---------------------------#
        #Create mesh
        self.create_mesh_button.clicked.connect(self._make_mesh)
        #Crop mesh
        self.cropMeshButton.clicked.connect(self.crop_mesh_box)
        #Change normals
        self.change_normals_button.clicked.connect(self.select_points_for_normals)
        #Save normals
        self.save_normals_button.clicked.connect(self.save_normals)
        #Fix mesh
        self.fix_mesh_button.clicked.connect(self.repair_mesh)
        #Triangles amount
        self.triangles_amount_input_field.setValidator(QIntValidator(1, 2147483647, self))
        self.triangles_amount_input_field.textChanged.connect(self._triangles_amount_changed)
        self.triangles_amount_checkbox.clicked.connect(self._enable_triangles_amount_input_field)

        # -------------------Normalization----------------------------#
        # Normalize button
        self.normalize_btn.clicked.connect(self.normalizeCloud)
        #Model iterations
        self.model_iterations_slider.valueChanged.connect(self._model_iterations_slider_change)
        #Prop iterations
        self.prop_iterations_slider.valueChanged.connect(self._prop_iteration_slider_changed)
        #Number of parts
        self.number_of_parts_slider.valueChanged.connect(self._number_of_parts_slider_changed)
        #Minimum points on path
        self.min_points_on_path_slider.valueChanged.connect(self._min_points_on_path_slider_changed)
        #Curvature treshold
        self.curvature_treshold_slider.valueChanged.connect(self.curvature_threshold_slider_changed)

        #-------------------Exports-----------------------------------#
        #OBJ
        self.export_to_obj.clicked.connect(lambda: self._on_export_to_obj(self.create_mesh))
        #STL
        self.export_to_stl.clicked.connect(lambda: self._on_export_to_stl(self.create_mesh))
        #PLY
        self.export_to_ply.clicked.connect(self._on_export_to_ply)

        #-------------------------------------------------------------#

        #Ram monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_memory_usage)
        monitor_thread.daemon = True
        monitor_thread.start()

    def monitor_memory_usage(self):
        process = psutil.Process()
        mem_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()
        total_memory = virtual_memory.total / (1024 * 1024 * 1024)
        while True:
            virtual_memory = psutil.virtual_memory()
            used_ram = round((virtual_memory.used / (1024 * 1024 * 1024)), 2)
            ram_usage = round(((used_ram * 100) / (total_memory - 0.5)), 0)
            self.memoryBar.setValue(int(ram_usage))
            if round((virtual_memory.available / (1024 * 1024)), 0) < 500:
                print("Insufficient free RAM")
                os.kill(os.getpid(), signal.SIGTERM)
            time.sleep(1)

def main():
    app = QApplication([])
    window = MyGUI()

    app.exec_()


if __name__ == '__main__':
    main()