"""
################################################################################################
||                                                                                            ||
||                                       Mesh Selection                                       ||
||                                                                                            ||
||                    This file contains functions for selecting the mesh                     ||
||                                                                                            ||
################################################################################################
"""
import copy
import open3d as o3d
import pyvista as pv
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
from pyvistaqt import QtInteractor

class MeshSelection():
    #Declaration of global variables for mesh and cloud available throughout the program
    idx_table = []              #Table of indices
    cloud_for_indicates = None  #Cloud in open3d
    #-----------------------------------------------------------------------------------

    #Function responsible for moving parts of the grid
    def move_sphere(self, point, i):
        # Assuming the mesh is a PolyData object
        # self.mesh.points[i] = point

        if self.idx_table is None:
            self.idx_table = []
            print(f"POINTTT   ", point)
            print(f"MESH POINTSSS    ", self.mesh.points[i])

            self._calc_prefer_indicate(point)
            print(f"idx_table[0]     ", self.idx_table[0])
            id = self.idx_table[0]

            print(f"IDD     ", id)
            # print(self.cloud.points)
            print(f"cloud.points[id]     ", self.mesh.points[id])

            iii = self.mesh.points[self.idx_table[0]] - 1
            self.mesh.points[iii] = point

        else:
            self.mesh.points[self.idx_table[0]] = point

    #Function responsible for generating spheres for mesh editing
    def select_area(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            #Preparation of an array of points returned by selecting an area
            points_array = picked.GetPoints().GetData()
            print('-----------------------------------------------')
            num_points = points_array.GetNumberOfTuples()
            points = [
                [points_array.GetComponent(i, 0), points_array.GetComponent(i, 1), points_array.GetComponent(i, 2)]
                for i in range(num_points)]
            self.picked_points = points
            # print(self.picked_points)
            #----------------------------------------------------------------

            #Calculation of indices for points.
            #Possibly redundant code
            for point in points:
                self._calc_prefer_indicate_mesh(point)
            #----------------------------------

            # print(f"fdfffffffffff",  self.idx_table)

            #Adding editing spheres to the plotter
            # self._calc_prefer_indicate_mesh(point)   # po jednym punkcie
            self.plotter.add_sphere_widget(callback=self.move_sphere, center=self.picked_points, radius=0.0010)
            #-------------------------------------


    #Function called from the gui which is responsible for selecting the editing area
    def _edit_mesh(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(callback=self.select_area, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    def _calc_prefer_indicate(self, point):
        # In the absence of an existing cloud in open3d, it is calculated.
        # This fragment is called once by the soft start located in the file functions
        # In each subsequent case, only else is called.
        if self.cloud_for_indicates is None:
            # Conversion of pyvist cloud to open3d
            pyvista_points = self.cloud.points
            points_open3d = o3d.utility.Vector3dVector(pyvista_points)
            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            # ------------------------------------

            # Maintaining the open3d cloud to reduce the number of calculations required
            self.cloud_for_indicates = copy.deepcopy(cloud_o3d)
            # --------------------------------------------------------------------------

            # Retrieve the previously saved open3d cloud to a local variable
            cloud = copy.deepcopy(self.cloud_for_indicates)
            # --------------------------------------------------------------

            # Point-to-vertex matching calculation
            cloud.points.append(np.asarray(point))
            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            self.idx_table.append(idx[-1])  # Saving the calculated index into an array
            # ------------------------------------
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


