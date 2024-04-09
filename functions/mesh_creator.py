"""
################################################################################################
||                                                                                            ||
||                                        Mesh Creator                                        ||
||                                                                                            ||
||             This file contains functions for generating and repairing the mesh             ||
||                                                                                            ||
################################################################################################
"""
import math
import os
import copy
import threading
import numpy as np
import sys
import pymeshfix
import open3d as o3d
import laspy
import pyvista as pv
from pyntcloud import PyntCloud
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MeshCreator():
    def _make_mesh(self):
        #Converting pyvista cloud to open3d cloud
        pyvista_points = self.cloud.points

        points_open3d = o3d.utility.Vector3dVector(pyvista_points)

        cloud = o3d.geometry.PointCloud()
        cloud.points = points_open3d
        #----------------------------------------

        #Normals calculation (not finished)
        if self.origin_vectors_normalized is None:
            cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        else:
            cloud.normals = o3d.utility.Vector3dVector(self.origin_vectors_normalized)
        #----------------------------------

        #Creating open3d mesh
        radii = [0.005, 0.01, 0.02, 0.04]
        rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud, o3d.utility.DoubleVector(radii))

        if self.settings.enable_triangles_amount_input_field:
            simplified_mesh = rec_mesh.simplify_quadric_decimation(target_number_of_triangles=int(self.settings.triangles_amount)) #Changing triangles amount
            rec_mesh = simplified_mesh

        if self.origin_vectors_normalized is None:
            pcd = rec_mesh.sample_points_poisson_disk(5000)

            pcd.normals = o3d.utility.Vector3dVector(np.zeros(
                (1, 3)))  # invalidate existing normals
        #----------------------

        #Saving cloud to temporary stl file (deleted after operation)
        filename = self.settings.file_path
        filename = filename[:-4] + "_temp.stl"

        try:
            o3d.io.write_triangle_mesh(filename, rec_mesh)
            print("[Info] Successfully exported to", filename)
        except Exception as e:
            print("[Error] An error occurred during the export:", str(e))
        #-------------------------------------------------------------

        #Reading temp file and deleting it
        self.create_mesh = pv.read(filename)
        os.remove(filename)
        #---------------------------------

        #Adding mesh to plotter with clearing
        try:
            self.plotter.remove_actor(self.mesh_geometry_container)
            self.plotter.remove_actor(self.mesh_with_triangles_container)
            if self.display_triangles_checkbox.isChecked():
                self.display_triangles_checkbox.setChecked(False)
        except:
            print("No existing mesh to remove")

        self.mesh_geometry_container = self.plotter.add_mesh(self.create_mesh)
        self.display_mesh_checkbox.setChecked(True)
        #----------------------

        #Activating export mesh buttons
        if self.create_mesh is not None:
            self.settings.enable_buttons_mesh = True
            self._apply_settings()
        #------------------------------

    def repair_mesh(self):
        cpos = [(-0.2, -0.13, 0.12), (-0.015, 0.10, -0.0), (0.28, 0.26, 0.9)]

        # Generate a meshfix mesh ready for fixing and extract the holes
        meshfix = pymeshfix.MeshFix(self.create_mesh)
        holes = meshfix.extract_holes()

        # Repair the mesh
        meshfix.repair(verbose=True)

        #Adding meshfix to plotter
        try:
            self.plotter.remove_actor(self.mesh_geometry_container)
            self.plotter.remove_actor(self.mesh_with_triangles_container)
            if self.display_triangles_checkbox.isChecked():
                self.display_triangles_checkbox.setChecked(False)
        except:
            print("No existing mesh to remove")

        self.mesh_geometry_container = self.plotter.add_mesh(meshfix.mesh)
        self.display_mesh_checkbox.setChecked(True)

        self.create_mesh = meshfix.mesh
        #-------------------------

        #Activating export mesh buttons
        if self.create_mesh is not None:
            self.settings.enable_buttons_mesh = True
            self._apply_settings()
        #------------------------------
