from libraries import *

class FileFunctions:

    cloud = None

    def _on_menu_open(self):
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Choose file to load",
                             self.window.theme)
        dlg.add_filter(".laz", "Compressed las (.laz)")
        dlg.add_filter(".las", "Cloud data (.las)")
        dlg.add_filter(".stl", "Stereolithography files (.stl)")
        dlg.add_filter(".obj", "Wavefront OBJ files (.obj)")
        dlg.add_filter(".ply", "Polygon files (.ply)")
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
                if extension == "ply":
                    self.cloud = o3d.io.read_point_cloud(path)
                else:
                    las_file = laspy.read(path)
                    points = np.vstack([las_file.x, las_file.y, las_file.z]).T
                    self.cloud = o3d.geometry.PointCloud()
                    self.cloud.points = o3d.utility.Vector3dVector(points)

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
                else:
                    # Point cloud
                    self._scene.scene.add_geometry("__model__", geometry,
                                                   self.settings.material)
                bounds = self._scene.scene.bounding_box
                self._scene.setup_camera(60, bounds, bounds.get_center())
            except Exception as e:
                print(e)

    def _on_export_to_obj(self, mesh):
        print(mesh)

    def _on_export_to_stl(self, mesh):
        print(mesh)