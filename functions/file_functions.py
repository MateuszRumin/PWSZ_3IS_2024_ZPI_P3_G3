import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import open3d as o3d
import laspy
import numpy as np
import pyvista as pv
from pyntcloud import PyntCloud
import pylas



class FileFunctions:

    cloud = None
    cloud_backup = None
    fileName = None



    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "LAS Files (*.las);;STL Files (*.stl);;LAZ Files (*.laz);;OBJ Files (*.obj);;All Files (*)"
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", filters, options=options)
        if self.fileName:
            self.settings.file_path = self.fileName
            self.load(self.fileName)

    def load(self, path):
        extension = path[-3:]

        self.plotter.clear()

        geometry = None
        mesh = None

        if extension == "ply" or extension == "pcd" or extension == "las" or extension == "laz":
            try:
                cloud = PyntCloud.from_file(path)
                geometry = cloud.to_instance("pyvista", mesh=False)
                self.cloud = geometry
                self.cloud_backup = self.cloud
            except Exception as e:
                print("[WARNING] Failed to read points", path, e)
        else:
            # Assuming the file is a mesh
            try:
                mesh = pv.read(path)
                self.mesh = mesh
                print("[Info] Successfully read", path)
            except Exception as e:
                print("[WARNING] Failed to read mesh", path, e)

        if geometry is not None:

            #Soft start for point matching function
            point = self.cloud.points[1]
            self._calc_prefer_indicate(point)

            #Add points to plotter
            self.plotter.add_points(self.cloud)

            # Update the plotter to display the new mesh
            self.plotter.update()

            self.settings.enable_buttons_cloud = True
            self._apply_settings()
        elif mesh is not None:
            self.create_mesh = mesh
            self.plotter.add_mesh(mesh, color='white', show_edges=True)
            self.settings.enable_buttons_cloud = True
            self._apply_settings()

        self.plotter.show()

    def _on_export_to_obj(self, mesh):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "OBJ Files (*.obj);;All Files (*)"
        self.fileName, _ = QFileDialog.getSaveFileName(self, "Save OBJ File", "", filters, options=options)

        if self.fileName:
            try:
                pv.save_meshio(self.fileName, self.create_mesh, file_format='obj')
            except Exception as e:
                print("[WARNING] Failed to save mesh", e)


    def _on_export_to_stl(self, mesh):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "STL Files (*.stl);;All Files (*)"
        self.fileName, _ = QFileDialog.getSaveFileName(self, "Save STL File", "", filters, options=options)

        if self.fileName:
            try:
                self.create_mesh.save(self.fileName)
            except Exception as e:
                print("[WARNING] Failed to save mesh", e)


    def _on_export_to_pcd(self):
        print("export to pcd")

    def _on_export_to_ply(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "PLY Files (*.ply);;All Files (*)"
        self.fileName, _ = QFileDialog.getSaveFileName(self, "Save PLY File", "", filters, options=options)

        if self.fileName:
            points = self.cloud.points
            vertices = np.array(points)

            with open(self.fileName, 'w') as f:
                f.write("ply\n")
                f.write("format ascii 1.0\n")
                f.write("element vertex %d\n" % len(vertices))
                f.write("property float x\n")
                f.write("property float y\n")
                f.write("property float z\n")
                f.write("end_header\n")
                for vertex in vertices:
                    f.write("%f %f %f\n" % (vertex[0], vertex[1], vertex[2]))