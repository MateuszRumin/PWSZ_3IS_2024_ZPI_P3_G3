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

class CloudSelection():
    idx_table = []
    cloud_for_indicates = None

    def showSelectedArea(self, picked):
        # ProgressBar
        self.progressBar.setValue(0)
        completed = 0

        #selection
        if isinstance(picked, pv.UnstructuredGrid):
            self.idx_table = []
            points_array = picked.GetPoints().GetData()
            num_points = points_array.GetNumberOfTuples()
            points = [points_array.GetTuple3(i) for i in range(num_points)]
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
                    completed += 1
                    percent_complete = (completed / len(rounded_points)) * 100
                    self.progressBar.setValue(int(percent_complete))

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
            self.selected_points_value.setText(str(len(rounded_points)))
        else:
            print("Zaznaczono coś innego niż siatkę.")

        print("points selected")
        self.plotter.update()

    def showSelectedPoints(self, picked):
        self.idx_table = []
        rounded_point = tuple(round(coord, 4) for coord in picked)
        self._calc_prefer_indicate(rounded_point)
        self.selected_points_value.setText("1")
        print(self.idx_table[0])

    def _select_points(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(self.showSelectedArea, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    def _delete_points(self):
        self.plotter.disable_picking()
        self.plotter.enable_point_picking(self.showSelectedPoints, style='surface',
                                          show_message=('Naciśnij P aby zaznaczyć punkt'))
        print("points deleted")

    def _delete_selected_points(self):
        if self.idx_table is not None:
            pyvista_points = self.cloud.points
            points_open3d = o3d.utility.Vector3dVector(pyvista_points)
            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            cloud_filtered = cloud_o3d.select_by_index(self.idx_table, invert=True)
            cloud_o3d = cloud_filtered
            points_open3d_to_pyvista = np.asarray(cloud_o3d.points)
            self.cloud = pv.PolyData(points_open3d_to_pyvista)
            self.plotter.clear()
            self.plotter.add_points(self.cloud)
            self.selected_points_value.setText("0")


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
