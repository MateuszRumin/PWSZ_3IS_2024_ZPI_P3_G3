import os
import pdal

from libraries import *

class FileFunctions:

    cloud = None
    cloud_backup = None

    def _on_menu_open(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load",
                             self.window.theme)
        dlg.add_filter(".laz", "Compressed las (.laz)")
        dlg.add_filter(".las", "Cloud data (.las)")
        dlg.add_filter(".stl", "Stereolithography files (.stl)")
        dlg.add_filter(".obj", "Wavefront OBJ files (.obj)")
        dlg.add_filter(".ply", "Polygon files (.ply)")
        dlg.add_filter(".pcd", "Point cloud files (.pcd)")
        dlg.add_filter("", "All files")

        # A file dialog MUST define on_cancel and on_done functions
        dlg.set_on_cancel(self._on_file_dialog_cancel)
        dlg.set_on_done(self._on_load_dialog_done)
        self.window.show_dialog(dlg)

    def _on_file_dialog_cancel(self):
        self.window.close_dialog()

    def _on_load_dialog_done(self, filename):
        self.window.close_dialog()
        self.load(filename)
        self._on_enable_buttons()
        self.settings.file_path = filename

    def _on_menu_quit(self):
        gui.Application.instance.quit()

    def load(self, path):
        extension = path[-3:]
        self._scene.scene.clear_geometry()

        geometry = None
        geometry_type = o3d.io.read_file_geometry_type(path)

        mesh = None
        if geometry_type & o3d.io.CONTAINS_TRIANGLES:
            mesh = o3d.io.read_triangle_model(path)
        if mesh is None:
            print("[Info]", path, "appears to be a point cloud")
            self.cloud = None
            try:
                if extension == "ply" or extension == "pcd":
                    self.cloud = o3d.io.read_point_cloud(path)
                    self.cloud_backup = self.cloud
                else:
                    las_file = laspy.read(path)
                    points = np.vstack([las_file.x, las_file.y, las_file.z]).T
                    self.cloud = o3d.geometry.PointCloud()
                    self.cloud.points = o3d.utility.Vector3dVector(points)
                    self.cloud_backup = self.cloud
                    voxel_cloud = self.cloud.voxel_down_sample(voxel_size=(float(self.settings.complement_slider_1_value)/10000))
                    self.cloud = voxel_cloud

                    print(self.cloud)

            except Exception:
                pass
            if self.cloud is not None:
                print("[Info] Successfully read", path)
                if not self.cloud.has_normals():
                    self.cloud.estimate_normals()
                self.cloud.normalize_normals()
                geometry = self.cloud
            else:
                print("[WARNING] Failed to read points", path)

        if geometry is not None or mesh is not None:
            try:
                if mesh is not None:
                    # Triangle model
                    self._scene.scene.add_model("__model__", mesh)
                    self._add_geometry_name("__model__")
                else:
                    # Point cloud
                    self._scene.scene.add_geometry("__model__", geometry,
                                                   self.settings.material)
                    self._add_geometry_name("__model__")
                bounds = self._scene.scene.bounding_box
                self._scene.setup_camera(60, bounds, bounds.get_center())
            except Exception as e:
                print(e)

    def _on_export_to_obj(self, mesh):
        if mesh is not None:
            try:
                dlg = gui.FileDialog(gui.FileDialog.SAVE, "Choose file to save",
                                     self.window.theme)
                dlg.add_filter(".obj", "Wavefront OBJ files (.obj)")
                dlg.add_filter("", "All files")
                dlg.set_on_cancel(self._on_file_dialog_cancel)
                dlg.set_on_done(self._on_export_dialog_done)
                self.window.show_dialog(dlg)
            except Exception as e:
                print("[Error] An error occurred while preparing the export:", str(e))
        else:
            print("[Warning] No mesh to export.")

    def _on_export_to_stl(self, mesh):
        if mesh is not None:
            try:
                dlg = gui.FileDialog(gui.FileDialog.SAVE, "Choose file to save",
                                     self.window.theme)
                dlg.add_filter(".stl", "Stereolithography files (.stl)")
                dlg.add_filter("", "All files")
                dlg.set_on_cancel(self._on_file_dialog_cancel)
                dlg.set_on_done(self._on_export_dialog_done)
                self.window.show_dialog(dlg)
            except Exception as e:
                print("[Error] An error occurred while preparing the export:", str(e))
        else:
            print("[Warning] No mesh to export.")
            # alert = gui.Dialog("No mesh to export.")
            # self.window.show_dialog(alert)

    def _on_export_to_pcd(self):
        if self.cloud is not None:
            try:
                dlg = gui.FileDialog(gui.FileDialog.SAVE, "Choose file to save",
                                     self.window.theme)
                dlg.add_filter(".pcd", "Point Cloud files (.pcd)")
                dlg.set_on_cancel(self._on_file_dialog_cancel)
                dlg.set_on_done(self._on_export_cloud_dialog_done)
                self.window.show_dialog(dlg)
            except Exception as e:
                print("[Error] An error occurred while preparing the export:", str(e))
        else:
            print("[Warning] No point cloud to export.")

    def _on_export_to_ply(self):
        if self.cloud is not None:
            try:
                dlg = gui.FileDialog(gui.FileDialog.SAVE, "Choose file to save",
                                     self.window.theme)
                dlg.add_filter(".ply", "Polygon files (.ply)")
                dlg.set_on_cancel(self._on_file_dialog_cancel)
                dlg.set_on_done(self._on_export_cloud_dialog_done)
                self.window.show_dialog(dlg)
            except Exception as e:
                print("[Error] An error occurred while preparing the export:", str(e))
        else:
            print("[Warning] No point cloud to export.")

    def _on_export_dialog_done(self, filename):
        self.window.close_dialog()
        if filename.endswith(".stl") or filename.endswith(".obj"):
            try:
                o3d.io.write_triangle_mesh(filename, self.create_mesh)
                print("[Info] Successfully exported to", filename)
            except Exception as e:
                print("[Error] An error occurred during the export:", str(e))
        else:
            print("[Warning] Invalid file format for export.")

    def _on_export_cloud_dialog_done(self, filename):
        self.window.close_dialog()
        #transform_matrix = self._scene.scene.get_geometry_transform("__model__")
        #transformed_point_cloud = self.cloud.transform(np.linalg.inv(transform_matrix))

        if filename.endswith(".ply") or filename.endswith(".pcd"):
            try:
                o3d.io.write_point_cloud(filename, self.cloud)
                print("[Info] Successfully exported to", filename)
            except Exception as e:
                print("[Error] An error occurred during the export:", str(e))

        else:
            print("[Warning] Invalid file format for export.")