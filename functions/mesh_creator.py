from libraries import *

from functions import create_gui_mesh

class MeshCreator(create_gui_mesh.CreateGuiMesh):
    create_mesh = None
    create_mesh_backup = None
    create_mesh_backup_backup = None
    def _make_mesh(self, path, points_number, max_points, normalize_points, cloud, voxel):
        # # Wczytaj plik LASer (LiDAR)
        # las_file = laspy.read(path)
        #
        # # Tworzenie chmury z pliku
        # points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        # cloud = o3d.geometry.PointCloud()
        # cloud.points = o3d.utility.Vector3dVector(points)


        # Obliczanie normalnych
        cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        radii = [0.005, 0.01, 0.02, 0.04]
        rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
            cloud, o3d.utility.DoubleVector(radii))

        pcd = rec_mesh.sample_points_poisson_disk(5000)

        pcd.voxel_down_sample(voxel_size=int(voxel))

        pcd.normals = o3d.utility.Vector3dVector(np.zeros(
            (1, 3)))  # invalidate existing normals

        self._scene.scene.add_geometry("__mesh__", rec_mesh, self.settings.material)
        self._add_geometry_name("__mesh__")

        self.create_mesh = rec_mesh
        self.create_mesh_backup = rec_mesh
        self.create_mesh_backup_backup = rec_mesh

        print("Path: " + str(path))
        print("Points: " + str(points_number))
        print("Max points: " + str(max_points))
        print("Normalize: " + str(normalize_points))
        print("Voxel: " + str(voxel))

        if self.create_mesh is not None:
            self._on_enable_buttons_export()

        #self.point_clouds(cloud)

