import copy
import pyvista as pv
import math
import copy
import threading
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import open3d as o3d
import laspy
import pyvista as pv
from pyntcloud import PyntCloud
from tqdm import tqdm

class NormalsSelection():
    _arrows = None

    def compute_vectors(self, mesh, point=np.array([0, 0, 0]), origin=True):
        if origin == False:
            manualorigin = point
            vectors = (mesh.points - manualorigin) * -1
            vectors = vectors / np.linalg.norm(vectors, axis=1)[:, None]
            return vectors
        elif origin == True:
            origin = mesh.center
            vectors = mesh.points - origin
            vectors = vectors / np.linalg.norm(vectors, axis=1)[:, None]
            return vectors

    def display_cloud_normals(self):
        vectors = self.compute_vectors(self.cloud)
        vectors[0:5, :]

        self.cloud['vectors'] = vectors
        sphere_center = np.array([0.0, 0.0, 0.0])

        arrows = self.cloud.glyph(
            orient='vectors',
            scale=False,
            factor=0.009,
        )

        self.plotter.clear()
        self._arrows = self.plotter.add_mesh(arrows, color='lightblue')
        self.plotter.add_sphere_widget(callback=self.callback, center=sphere_center, radius=0.01)

    def callback(self, point):
        print(f"x:", round(point[0], 4))
        print(f"y", round(point[1], 4))
        print(f"z:", round(point[2], 4))

        if point[0] != 0 or point[1] != 0 or point[2] != 0:
            self.plotter.remove_actor(self._arrows)
            vectors = self.compute_vectors(self.cloud, point, False)
            vectors[0:5, :]

            self.cloud['vectors'] = vectors
            sphere_center = np.array([0.0, 0.0, 0.0])

            arrows = self.cloud.glyph(
                orient='vectors',
                scale=False,
                factor=0.009,
            )
            self._arrows = self.plotter.add_mesh(arrows, color='lightblue')


