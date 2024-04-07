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
    _selected_normals_cloud = None
    _origin_vectors = None
    idx_table = []
    completed = 0
    origin_vectors_normalized = None


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
        vectors = self.compute_vectors(self._selected_normals_cloud)
        vectors[0:5, :]

        self._selected_normals_cloud['vectors'] = vectors
        sphere_center = np.array([0.0, 0.0, 0.0])

        arrows = self._selected_normals_cloud.glyph(
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
            vectors = self.compute_vectors(self._selected_normals_cloud, point, False)
            vectors[0:5, :]

            self._selected_normals_cloud['vectors'] = vectors
            sphere_center = np.array([0.0, 0.0, 0.0])

            arrows = self._selected_normals_cloud.glyph(
                orient='vectors',
                scale=False,
                factor=0.009,
            )
            self._arrows = self.plotter.add_mesh(arrows, color='lightblue')


    def select_normals_area(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            self.progressBar.setValue(0)
            self.completed = 0

            points_array = picked.GetPoints().GetData()
            print('-----------------------------------------------')
            num_points = points_array.GetNumberOfTuples()
            points = [
                [points_array.GetComponent(i, 0), points_array.GetComponent(i, 1), points_array.GetComponent(i, 2)]
                for i in range(num_points)]
            rounded_points = [tuple(round(coord, 4) for coord in point) for point in points]

            # Create a progress bar
            with tqdm(total=len(rounded_points), desc="Processing points") as pbar:
                threads = []
                for point in rounded_points:
                    thread = threading.Thread(target=self._calc_prefer_indicate, args=(point,))
                    thread.start()
                    threads.append(thread)

                    # Update the progress bar after each thread starts
                    pbar.update(1)
                    self.completed += 1
                    percent_complete = (self.completed / len(rounded_points)) * 100
                    self.progressBar.setValue(int(percent_complete))

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()

            self._selected_normals_cloud = pv.PolyData(points)
            self.display_cloud_normals()

    def select_points_for_normals(self):
        if self.cloud is not None:
            if self.settings.normals_computed_for_origin == False:
                self._origin_vectors = self.compute_vectors(self.cloud)
                self.settings.normals_computed_for_origin = True

            self.plotter.clear()
            self.idx_table = []

            self.plotter.add_mesh(self.cloud)
            self.plotter.disable_picking()
            self.plotter.enable_cell_picking(callback=self.select_normals_area, style='surface',
                                             show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    def save_normals(self):
        i = 0
        for idx in self.idx_table:
            if i == self.completed:
                break
            elif idx == self.cloud.n_points:
                print("?")
            elif i < len(self._selected_normals_cloud['vectors']):
                self._origin_vectors[idx] = self._selected_normals_cloud['vectors'][i]
                i += 1
            else:
                print(f"Index {i} is out of bounds for the vectors list.")
                break

        #self._origin_vectors[0:5, :]

        self.cloud['vectors'] = self._origin_vectors

        arrows = self.cloud.glyph(
            orient='vectors',
            scale=False,
            factor=0.009,
        )
        self.plotter.clear()
        self._arrows = self.plotter.add_mesh(arrows, color='lightblue')
        self.display_normals_checkbox.setChecked(True)
        self.origin_vectors_normalized = self._origin_vectors / np.linalg.norm(self._origin_vectors, axis=1)[:, np.newaxis]

    def _calc_prefer_indicate(self, point):
        if self.cloud_for_indicates is None:
            pyvista_points = self.cloud.points

            points_open3d = o3d.utility.Vector3dVector(pyvista_points)

            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            self.cloud_for_indicates = copy.deepcopy(cloud_o3d)

            cloud = copy.deepcopy(self.cloud_for_indicates)

            cloud.points.append(np.asarray(point))

            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            #return idx[-1]
            self.idx_table.append(idx[-1])
        else:
            cloud = copy.deepcopy(self.cloud_for_indicates)

            cloud.points.append(np.asarray(point))

            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            # return idx[-1]
            self.idx_table.append(idx[-1])


