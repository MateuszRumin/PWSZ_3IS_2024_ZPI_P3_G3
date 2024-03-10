from libraries import *

class PointEditor:
    def _edit_points(self, path):
        # Wczytaj plik LASer (LiDAR)
        las_file = laspy.read(path)

        # Tworzenie chmury z pliku
        points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        cloud = o3d.geometry.PointCloud()
        cloud.points = o3d.utility.Vector3dVector(points)

        # Obliczanie normalnych
        cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        o3d.visualization.draw_geometries_with_editing([cloud])
