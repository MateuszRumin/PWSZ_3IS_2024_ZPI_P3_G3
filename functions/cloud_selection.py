"""
################################################################################################
||                                                                                            ||
||                                      Cloud Selection                                       ||
||                                                                                            ||
||              This file is responsible for selecting and deleting cloud points              ||
||                                                                                            ||
################################################################################################
"""
import copy
import pyvista as pv
import math
import threading
import numpy as np
import sys
import open3d as o3d
import laspy
from pyntcloud import PyntCloud
from tqdm import tqdm
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class CloudSelection():
    #Declaration of global variables for point indicates
    idx_table = []
    cloud_for_indicates = None
    #---------------------------------------------------

    def showSelectedArea(self, picked):
        #Resetting the progress bar
        self.progressBar.setValue(0)
        completed = 0
        #-------------------------

        #-------------------------------Point selection-------------------------------------#
        if isinstance(picked, pv.UnstructuredGrid):
            self.idx_table = []             #Resetting the index
            self.cloud_for_indicates = None #Resetting open3d cloud

            #Preparation and rounding to four decimal places of the marked points
            points_array = picked.GetPoints().GetData()
            num_points = points_array.GetNumberOfTuples()
            points = [points_array.GetTuple3(i) for i in range(num_points)]
            rounded_points = [tuple(round(coord, 4) for coord in point) for point in points]
            #--------------------------------------------------------------------

            #Calling a function that matches marked points to vertices on threads with a progress indicator from the tqdm library
            with tqdm(total=len(rounded_points), desc="Processing points") as pbar:
                threads = []
                for point in rounded_points:
                    #Calculation statement
                    thread = threading.Thread(target=self._calc_prefer_indicate, args=(point,))
                    #---------------------

                    #Running the calculations
                    thread.start()
                    threads.append(thread)
                    #------------------------

                    # Update the progress bar after each thread starts
                    pbar.update(1)
                    completed += 1
                    percent_complete = (completed / len(rounded_points)) * 100
                    self.progressBar.setValue(int(percent_complete))
                    #-------------------------------------------------

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                #---------------------------------
            #---------------------------------------------------------------------------------------------------------------------
            self.selected_points_value.setText(str(len(rounded_points)))    #Display in the gui of the number of marked points
        else:
            print("Something other than a cloud was marked.")
        print("points selected")
        self.plotter.update()
        self.delete_selected_points_button.setEnabled(True)
        #-----------------------------------------------------------------------------------#


    #Function displaying a single marked point
    def showSelectedPoints(self, picked):
        self.idx_table = []              # Resetting indicates table
        self.cloud_for_indicates = None  # Resetting open3d cloud
        rounded_point = tuple(round(coord, 4) for coord in picked)
        self._calc_prefer_indicate(rounded_point)
        self.selected_points_value.setText("1")
        print(self.idx_table[0])
        self.delete_selected_points_button.setEnabled(True)     #Activating delete points button

    #Marking function
    def _select_points(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(self.showSelectedArea, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    #Function to mark a single point
    def _select_single_point(self):
        self.plotter.disable_picking()
        self.plotter.enable_point_picking(self.showSelectedPoints, style='surface',
                                          show_message=('Naciśnij P aby zaznaczyć punkt'))

    #Function to delete marked points
    def _delete_selected_points(self):
        if self.idx_table is not None:
            #Cloud conversion from pyvist to open3d
            pyvista_points = self.cloud.points
            points_open3d = o3d.utility.Vector3dVector(pyvista_points)
            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            #---------------------------------------

            #Filtering the cloud by deleted points
            cloud_filtered = cloud_o3d.select_by_index(self.idx_table, invert=True)
            cloud_o3d = cloud_filtered
            #-------------------------------------

            #Conversion of filtered open3d cloud to pyvista
            points_open3d_to_pyvista = np.asarray(cloud_o3d.points)
            self.cloud = pv.PolyData(points_open3d_to_pyvista)
            self.cloud_backup = copy.deepcopy(self.cloud)
            #----------------------------------------------

            #Re-loading the cloud to the plotter
            self.plotter.remove_actor(self.cloud_geometry_container)
            self.cloud_geometry_container = self.plotter.add_points(self.cloud)
            self.selected_points_value.setText("0")
            #-----------------------------------

            self.delete_selected_points_button.setEnabled(False)    #Deactivating delete points button


    #Point-to-vertex matching function (super inefficient)
    def _calc_prefer_indicate(self, point):
        #In the absence of an existing cloud in open3d, it is calculated.
        #This fragment is called once by the soft start located in the file functions
        #In each subsequent case, only else is called.
        if self.cloud_for_indicates is None:
            #Conversion of pyvist cloud to open3d
            pyvista_points = self.cloud.points
            points_open3d = o3d.utility.Vector3dVector(pyvista_points)
            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            #------------------------------------

            #Maintaining the open3d cloud to reduce the number of calculations required
            self.cloud_for_indicates = copy.deepcopy(cloud_o3d)
            #--------------------------------------------------------------------------

            #Retrieve the previously saved open3d cloud to a local variable
            cloud = copy.deepcopy(self.cloud_for_indicates)
            #--------------------------------------------------------------

            #Point-to-vertex matching calculation
            cloud.points.append(np.asarray(point))
            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            self.idx_table.append(idx[-1])  #Saving the calculated index into an array
            #------------------------------------
        else:
            # Retrieve the previously saved open3d cloud to a local variable
            cloud = copy.deepcopy(self.cloud_for_indicates)
            # --------------------------------------------------------------

            # Point-to-vertex matching calculation
            cloud.points.append(np.asarray(point))
            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            self.idx_table.append(idx[-1])  # Saving the calculated index into an array
            # ------------------------------------
