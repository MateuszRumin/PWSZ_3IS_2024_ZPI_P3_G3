import copy
import pyvista as pv
import math
import copy
import threading
import numpy as np
import sys
import open3d as o3d
import laspy
import pyvista as pv
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from pyntcloud import PyntCloud
from tqdm import tqdm
from normalization.orient import orient_normal,orient_large


class NormalizationClass():
    def normalizeCloud(self):
        #Getting values from settings
        model_iterations = self.settings.model_iterations_value
        prop_iterations = self.settings.prop_iterations_value
        number_of_parts = self.settings.number_of_parts_value
        min_points_on_path = self.settings.min_points_on_path_value
        curvature_threshold = self.settings.curvature_threshold_value / 100
        neighbours = self.settings.neighbours_value

        print("Normalization")
        print(f"Model iterations: ", model_iterations)
        print(f"Prop iterations: ", prop_iterations)
        print(f"Number of parts: ", number_of_parts)
        print(f"Minimum points on path: ", min_points_on_path)
        print(f"Curvature threshold: ", curvature_threshold)
        print(f"neighbours: ", neighbours)

        # neighbours = 50
        # #----------------------------
        # model_iterations = 5
        # prop_iterations = 3
        # number_of_parts = 30
        # min_points_on_path = 100
        # curvature_threshold = 0.01

        if self.cloud.points.any():
            # ptc = o3d.geometry.PointCloud()
            points = self.cloud.points
            # ptc.points = o3d.utility.Vector3dVector(points)
            # num_points = len(points)
            # if num_points < 100000:
            #    orient_normal(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,neighbours=30)
            # else:
            ptc = orient_large(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,neighbours)
            # ptc.points = o3d.utility.Vector3dVector(np.asarray(ptc.points)*1.7)
            # ptc.normals = o3d.utility.Vector3dVector(np.asarray(ptc.normals) * 1.7)
            #o3d.visualization.draw_geometries([ptc])
            # print(f"ptc points", np.asarray(ptc.points))
            # print(f"ptc normals", np.asarray(ptc.normals))
            self._origin_vectors = ptc.normals
            self.cloud['vectors'] = self._origin_vectors
            self.settings.normals_computed_for_origin == True
            # ptc.normals = o3d.utility.Vector3dVector(norm)
            self.open3d_normalized_cloud = ptc





