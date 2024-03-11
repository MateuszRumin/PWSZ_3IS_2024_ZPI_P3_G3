from libraries import *

class MeshCreator:
    def _make_mesh(self, path, points_number, max_points, normalize_points):
        # Wczytaj plik LASer (LiDAR)
        las_file = laspy.read(path)

        # Tworzenie chmury z pliku
        points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        cloud = o3d.geometry.PointCloud()
        cloud.points = o3d.utility.Vector3dVector(points)

        # Obliczanie normalnych
        cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        radii = [0.005, 0.01, 0.02, 0.04]
        rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            cloud, o3d.utility.DoubleVector(radii))

        pcd = rec_mesh.sample_points_poisson_disk(5000)
        pcd.normals = o3d.utility.Vector3dVector(np.zeros(
            (1, 3)))  # invalidate existing normals

        self._scene.scene.add_geometry("__mesh__", rec_mesh, self.settings.material)

        print("Points: " + str(points_number))
        print("Max points: " + str(max_points))
        print("Normalize: " + str(normalize_points))