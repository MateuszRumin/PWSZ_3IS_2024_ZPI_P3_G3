from libraries import *

from functions import create_gui_mesh

class MeshCreator(create_gui_mesh.CreateGuiMesh):
    create_mesh = None
    create_mesh_backup = None
    def _make_mesh(self, path, points_number, max_points, normalize_points, cloud, voxel):
        # # Wczytaj plik LASer (LiDAR)
        las_file = laspy.read(path)
        #
        # # Tworzenie chmury z pliku
        points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        cloud = o3d.geometry.PointCloud()
        cloud.points = o3d.utility.Vector3dVector(points)

        avg_distance = np.mean(cloud.compute_nearest_neighbor_distance())
        max_distance = np.max(cloud.compute_nearest_neighbor_distance())
        min_distance = np.min(cloud.compute_nearest_neighbor_distance())

        scale_points = 1.01
        scaled_points = points * scale_points
        center = np.mean(points, axis=0)
        center2 = np.mean(scaled_points, axis=0)
        dierence_center = center2 - center
        scaled_points = scaled_points - dierence_center

        cloud2 = o3d.geometry.PointCloud()
        cloud2.points = o3d.utility.Vector3dVector(scaled_points)
        normals = scaled_points - points
        normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
        cloud.normals = o3d.utility.Vector3dVector(normals)

        par = avg_distance

        rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud, depth=8, width=0,
                                                                             linear_fit=False, n_threads=4)
        final = rec_mesh[0]
        final = final.sample_points_poisson_disk(100000)
        final.paint_uniform_color([0, 0, 1])

        radii = [0.9 * par, 0.91 * par, 0.92 * par, 0.93 * par, 0.94 * par, 0.95 * par, 0.96 * par, 0.97 * par,
                 0.98 * par, 0.99 * par,
                 1 * par, 1.01 * par, 1.02 * par, 1.03 * par, 1.04 * par, 1.05 * par, 1.06 * par, 1.07 * par,
                 1.08 * par, 1.09 * par,
                 1.1 * par, 1.11 * par, 1.12 * par, 1.13 * par, 1.14 * par, 1.15 * par, 1.16 * par, 1.17 * par,
                 1.18 * par, 1.19 * par,
                 1.2 * par, 1.21 * par, 1.22 * par, 1.23 * par, 1.24 * par, 1.25 * par, 1.26 * par, 1.27 * par,
                 1.28 * par, 1.29 * par,
                 1.3 * par, 1.4 * par, 1.5 * par, 1.6 * par, 1.75 * par]
        radii_double_vector = o3d.utility.DoubleVector(radii)
        rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(final, radii_double_vector)
        rec_mesh.compute_vertex_normals()





        self._scene.scene.add_geometry("__mesh__", rec_mesh, self.settings.material)
        self._add_geometry_name("__mesh__")

        self.create_mesh = rec_mesh
        self.create_mesh_backup = rec_mesh



        if self.create_mesh is not None:
            self._on_enable_buttons_export()

        #self.point_clouds(cloud)

