import numpy as np

from libraries import *

class PointEditor:
    def _edit_points(self, path):
        # Wczytaj plik LASer (LiDAR)
        las_file = laspy.read(path)

        # Tworzenie chmury z pliku
        points = np.vstack([las_file.x, las_file.y, las_file.z]).T
        cloud = o3d.geometry.PointCloud()
        cloud.points = o3d.utility.Vector3dVector(points)
        print(np.asarray(cloud.points[1]))

        print(cloud)
        # Filtracja punktów
        # Filtracja punktów
        filtered_indices = [idx for idx, point in enumerate(cloud.points) if
                            point[1] <= 0]  # Sprawdzamy współrzędną y (indeks 1)
        cloud_filtered = cloud.select_by_index(filtered_indices)
        cloud = cloud_filtered
        print(cloud)

        # Obliczanie normalnych
        cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

        o3d.visualization.draw_plotly([cloud])
