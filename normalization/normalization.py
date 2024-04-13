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
        curvature_threshold = self.settings.curvature_threshold_value
        n = 30
        #----------------------------

        if self.cloud.points.any():
            points = self.cloud.points
            num_points = len(points)
            # if num_points < 100000:
            #    orient_normal(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,n=30)
            # else:
            orient_large(points,model_iterations,prop_iterations,number_of_parts,min_points_on_path,curvature_threshold,n)




        # print("Normalization")
        # print(f"Model iterations: ", model_iterations)
        # print(f"Prop iterations: ", prop_iterations)
        # print(f"Number of parts: ", number_of_parts)
        # print(f"Minimum points on path: ", min_points_on_path)
        # print(f"Curvature threshold: ", curvature_threshold)