"""
################################################################################################
||                                                                                            ||
||                                        Mesh Creator                                        ||
||                                                                                            ||
||             This file contains functions for generating and repairing the mesh             ||
||                                                                                            ||
################################################################################################
"""
import os
import copy
import numpy as np
import pymeshfix
import open3d as o3d
import pyvista as pv


class MeshCreator():
    def _make_mesh(self):
        if self.create_mesh is not None and self.cloud is None:
            self.transform_existing_mesh()
        elif self.normalize_checkbox.isChecked():
            self.normalizeCloud()
            cloud = self.open3d_normalized_cloud

            par = np.mean(cloud.compute_nearest_neighbor_distance())

            # Creating open3d mesh
            radii = [0.005, 0.01, 0.015, 0.02, 0.025]
            # radii = [0.9 * par, 0.91 * par, 0.92 * par, 0.93 * par, 0.94 * par, 0.95 * par, 0.96 * par, 0.97 * par,
            #          0.98 * par, 0.99 * par,
            #          1 * par, 1.01 * par, 1.02 * par, 1.03 * par, 1.04 * par, 1.05 * par, 1.06 * par, 1.07 * par,
            #          1.08 * par, 1.09 * par,
            #          1.1 * par, 1.11 * par, 1.12 * par, 1.13 * par, 1.14 * par, 1.15 * par, 1.16 * par, 1.17 * par,
            #          1.18 * par, 1.19 * par,
            #          1.2 * par, 1.21 * par, 1.22 * par, 1.23 * par, 1.24 * par, 1.25 * par, 1.26 * par, 1.27 * par,
            #          1.28 * par, 1.29 * par,
            #          1.3 * par, 1.4 * par, 1.5 * par, 1.6 * par, 1.75 * par, 0.01, 0.02, 0.04]
            rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud,
                                                                                       o3d.utility.DoubleVector(radii))

            # rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud, depth=6, linear_fit=False, n_threads=4 )
            #
            # rec_mesh = o3d.geometry.TriangleMesh(rec_mesh[0])

            if self.settings.enable_triangles_amount_input_field:
                triangles_amount = len(rec_mesh.triangles)
                triangles_amount_calculated = (triangles_amount * (self.settings.triangles_amount / 100))
                simplified_mesh = rec_mesh.simplify_quadric_decimation(
                    target_number_of_triangles=int(triangles_amount_calculated))  # Changing triangles amount
                rec_mesh = simplified_mesh

            if self.origin_vectors_normalized is None:
                pcd = rec_mesh.sample_points_poisson_disk(5000)

                pcd.normals = o3d.utility.Vector3dVector(np.zeros(
                    (1, 3)))  # invalidate existing normals
            # ----------------------

            # Saving cloud to temporary stl file (deleted after operation)
            filename = self.settings.file_path
            filename = filename[:-4] + "_temp.stl"

            try:
                o3d.io.write_triangle_mesh(filename, rec_mesh)
                print("[Info] Successfully exported to", filename)
            except Exception as e:
                print("[Error] An error occurred during the export:", str(e))
            # -------------------------------------------------------------

            # Reading temp file and deleting it
            self.create_mesh = pv.read(filename)
            self.create_mesh_backup = self.create_mesh
            os.remove(filename)
            # ---------------------------------

            self.remove_mesh()
            self.add_mesh_to_plotter(self.create_mesh)
            # ------------------------------
        else:
            # Converting pyvista cloud to open3d cloud
            pyvista_points = self.cloud.points

            points_open3d = o3d.utility.Vector3dVector(pyvista_points)

            cloud = o3d.geometry.PointCloud()
            cloud.points = points_open3d
            # ----------------------------------------

            # Normals calculation (not finished)
            if self.origin_vectors_normalized is None:
                cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
            else:
                cloud.normals = o3d.utility.Vector3dVector(self.origin_vectors_normalized)
            # ----------------------------------

            # Creating open3d mesh
            radii = [0.005, 0.01, 0.02, 0.04]
            rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud,
                                                                                       o3d.utility.DoubleVector(radii))

            if self.settings.enable_triangles_amount_input_field:
                triangles_amount = len(rec_mesh.triangles)
                triangles_amount_calculated = (triangles_amount * (self.settings.triangles_amount / 100))
                simplified_mesh = rec_mesh.simplify_quadric_decimation(
                    target_number_of_triangles=int(triangles_amount_calculated))  # Changing triangles amount
                rec_mesh = simplified_mesh

            if self.origin_vectors_normalized is None:
                pcd = rec_mesh.sample_points_poisson_disk(5000)

                pcd.normals = o3d.utility.Vector3dVector(np.zeros(
                    (1, 3)))  # invalidate existing normals
            # ----------------------

            # Saving cloud to temporary stl file (deleted after operation)
            filename = self.settings.file_path
            filename = filename[:-4] + "_temp.stl"

            try:
                o3d.io.write_triangle_mesh(filename, rec_mesh)
                print("[Info] Successfully exported to", filename)
            except Exception as e:
                print("[Error] An error occurred during the export:", str(e))
            # -------------------------------------------------------------

            # Reading temp file and deleting it
            self.create_mesh = pv.read(filename)
            self.create_mesh_backup = self.create_mesh
            os.remove(filename)
            # ---------------------------------

            # Reloading mesh
            self.remove_mesh()
            self.add_mesh_to_plotter(self.create_mesh)
            # ------------------------------

    def repair_mesh(self):
        #cpos = [(-0.2, -0.13, 0.12), (-0.015, 0.10, -0.0), (0.28, 0.26, 0.9)]

        # Generate a meshfix mesh ready for fixing and extract the holes
        meshfix = pymeshfix.MeshFix(self.create_mesh)
        holes = meshfix.extract_holes()

        # Repair the mesh
        meshfix.repair(verbose=True)
        self.create_mesh = meshfix.mesh
        self.create_mesh_backup = self.create_mesh

        # Reloading mesh
        self.remove_mesh()
        self.add_mesh_to_plotter(self.create_mesh)
        #------------------------------

    def transform_existing_mesh(self):
        #Triangles reduction
        print(f"Number of triangles in mesh: {self.create_mesh.n_points}")
        if self.settings.enable_triangles_amount_input_field:
            self.create_mesh = copy.deepcopy(self.create_mesh_backup)
            reduction_value = ((float(self.settings.triangles_amount) - 100) * (-1)) / 100
            if reduction_value < 1:
                self.create_mesh = self.create_mesh.decimate(reduction_value)
        print(f"Number of triangles in mesh after reduction: {self.create_mesh.n_points}")

        # Reloading mesh
        self.remove_mesh()
        self.add_mesh_to_plotter(self.create_mesh)
        # ------------------------------