from libraries import *

class MeshCreator:
    create_mesh = None
    def _make_mesh(self, path, points_number, max_points, normalize_points, cloud):
        # # Wczytaj plik LASer (LiDAR)
        las_file = laspy.read(path)
        #
        # # Tworzenie chmury z pliku
        points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        # cloud = o3d.geometry.PointCloud()
        # cloud.points = o3d.utility.Vector3dVector(points)



        # Obliczanie normalnych
        # cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        avg_distance = np.mean(cloud.compute_nearest_neighbor_distance())
        max_distance = np.max(cloud.compute_nearest_neighbor_distance())
        min_distance = np.min(cloud.compute_nearest_neighbor_distance())

        center = np.mean(points, axis=0)
        normals = points - center
        normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
        cloud.normals = o3d.utility.Vector3dVector(normals)

        par = avg_distance
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
        rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud, radii_double_vector)
        rec_mesh.compute_vertex_normals()

        self._scene.scene.add_geometry("__mesh__", rec_mesh, self.settings.material)

        self.create_mesh = rec_mesh

        print("Path: " + str(path))
        print("Points: " + str(points_number))
        print("Max points: " + str(max_points))
        print("Normalize: " + str(normalize_points))

        if self.create_mesh is not None:
            self._on_enable_buttons_export()