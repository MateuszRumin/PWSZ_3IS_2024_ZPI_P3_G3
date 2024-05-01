import numpy as np
import pyntcloud
import pyvista as pv
import tempfile

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from pyntcloud import PyntCloud
from stl import mesh    #pip install numpy-stl
from memory_profiler import profile


class ThreadFunctionsRedirections:
    def assign_cloud(self, cloud):
        QCoreApplication.processEvents()
        self.cloud = cloud

    def assign_mesh(self, mesh):
        QCoreApplication.processEvents()
        self.create_mesh = mesh

    def remove_actor_slot(self, actor):
        QCoreApplication.processEvents()

        if actor == "cloud":
            self.remove_cloud()
        elif actor == "normals":
            self.remove_normals()
        elif actor == "mesh":
            self.remove_mesh()
        elif actor == "mesh_with_triangles":
            self.remove_mesh_with_triangles()
        elif actor == "all_geometries":
            self.remove_all_geometries_from_plotter()

    def reset_plotter_slot(self):
        QCoreApplication.processEvents()
        self._reset_plotter()
        self.close_loading_window()

    def add_cloud_slot(self, cloud):
        QCoreApplication.processEvents()
        self.add_cloud_to_plotter(cloud)
        self.close_loading_window()

    def add_mesh_slot(self, mesh):
        QCoreApplication.processEvents()
        self.add_mesh_to_plotter(mesh)
        self.close_loading_window()

    def add_mesh_with_triangles_slot(self, mesh_with_triangles):
        QCoreApplication.processEvents()
        self.add_mesh_with_triangles_to_plotter(mesh_with_triangles)
        self.close_loading_window()

    def clear_before_load(self):
        QCoreApplication.processEvents()
        self.remove_all_geometries_from_plotter()  # Clearing plotter
        self.normalization_preset_combobox.clear()  # Clear normalizations presets

        # Clearing variables for clouds and meshes in case of reloading
        self.cloud = None
        self.cloud_backup = tempfile.TemporaryFile()
        self.create_mesh = None
        self.create_mesh_backup = tempfile.TemporaryFile()
        self.settings.normals_computed_for_origin = False
        # -------------------------------------------------------------

    def overwrite_backup_cloud(self, cloud):
        QCoreApplication.processEvents()
        with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
            cloud.save(self.cloud_backup.name)

    def overwrite_backup_mesh(self, mesh):
        QCoreApplication.processEvents()
        with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
            mesh.save(self.create_mesh_backup.name)