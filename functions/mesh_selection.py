import copy
import open3d as o3d
import pyvista as pv
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
from pyvistaqt import QtInteractor


class MeshSelection():
    idx_table = []
    cloud_for_indicates = None
    _point = None
    selected_mesh = []

    def move_sphere(self, point, i):
        # Assuming the mesh is a PolyData object
        # self.mesh.points[i] = point

        if self.idx_table is not None:
            self.idx_table = []
            print(f"POINTTT   ", point)
            print(f"MESH POINTSSS    ", self.mesh.points[i])

            self._calc_prefer_indicate(point)
            print(f"idx_table[0]     ", self.idx_table[0])
            id = self.idx_table[0]

            print(f"IDD     ", id)
            # print(self.cloud.points)
            print(f"cloud.points[id]     ", self.mesh.points[id])

            # iii = self.mesh.points[self.idx_table[0]] - 1
            # self.mesh.points[iii] = point
            self.mesh.points[self.idx_table[0]] = point

        else:
            self.mesh.points[self.idx_table[0]] = point


    def select_area(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            points_array = picked.GetPoints().GetData()
            print('-----------------------------------------------')
            num_points = points_array.GetNumberOfTuples()
            points = [
                [points_array.GetComponent(i, 0), points_array.GetComponent(i, 1), points_array.GetComponent(i, 2)]
                for i in range(num_points)]
            self.picked_points = points
            # print(self.picked_points)

            for point in points:
                self._calc_prefer_indicate_mesh(point)

            self.selected_mesh = points

            # print(f"fdfffffffffff",  self.idx_table)
            # self._calc_prefer_indicate_mesh(point)   # po jednym punkcie

            self.plotter.add_sphere_widget(callback=self.move_sphere, center=self.picked_points, radius=0.0010)

    def _edit_mesh(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(callback=self.select_area, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    def _calc_prefer_indicate_mesh(self, point):
        if self.cloud_for_indicates is None:
            pyvista_points = self.mesh.points

            points_open3d = o3d.utility.Vector3dVector(pyvista_points)

            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            self.cloud_for_indicates = copy.deepcopy(cloud_o3d)

            cloud = copy.deepcopy(self.cloud_for_indicates)

            cloud.points.append(np.asarray(point))

            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            # return idx[-1]
            self.idx_table.append(idx[-1])
        else:
            cloud = copy.deepcopy(self.cloud_for_indicates)

            cloud.points.append(np.asarray(point))

            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            # return idx[-1]
            self.idx_table.append(idx[-1])


