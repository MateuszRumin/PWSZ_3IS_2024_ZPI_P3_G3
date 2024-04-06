
import laspy
import open3d as o3d
import numpy as np
import copy
from scipy.spatial import Delaunay
import pyvista as pv
import pymeshfix as mf
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans

def load_mesh(file_path):
    if file_path.lower().endswith('.stl'):
        mesh = pv.read(file_path)
    return mesh

def segment_point_cloud(points, num_clusters=100):
    # Inicjalizacja i dopasowanie modelu KMeans
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(points)

    # Przypisanie klastrów do punktów
    labels = kmeans.labels_

    # Tworzenie pustej chmury punktów dla każdego klastra
    clusters = [o3d.geometry.PointCloud() for _ in range(num_clusters)]

    # Dodanie punktów do odpowiednich chmur punktów klastrów
    for i, point in enumerate(points):
        cluster_idx = labels[i]
        clusters[cluster_idx].points.append(point)

    # Konwersja chmur punktów do listy obiektów Open3D
    clusters_open3d = [o3d.geometry.PointCloud() for _ in range(num_clusters)]
    for i, cluster in enumerate(clusters):
        clusters_open3d[i].points = o3d.utility.Vector3dVector(np.asarray(cluster.points))

    return clusters_open3d

def compute_normals(points, k=50):

    nbrs = NearestNeighbors(n_neighbors=k, algorithm='kd_tree').fit(points)

    distances, indices = nbrs.kneighbors(points)

    normals = []
    for i in range(len(points)):

        neighbor_points = points[indices[i]]
        cov_matrix = np.cov(neighbor_points, rowvar=False)

        # Oblicz wartości i wektory własne macierzy kowariancji
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

        # Wybierz wektor własny odpowiadający najmniejszej wartości własnej
        normal = eigenvectors[:, np.argmin(eigenvalues)]

        # Ustaw kierunek wektora normalnego do zawsze wskazywał na zewnątrz powierzchni
        if normal.dot(points[i]) < 0:
            normal *= -1
        elif normal.dot(points[i]) == 0:
            normal *= -1



        normals.append(normal)

    return np.array(normals)

las_file = laspy.read("./data/bunny.laz")
points = np.vstack([las_file.x, las_file.y, las_file.z]).T
cloud = o3d.geometry.PointCloud()
cloud.points = o3d.utility.Vector3dVector(points)
# voxel_size = 0.05  # Adjust as needed
# downsampled_cloud = cloud.voxel_down_sample(voxel_size)
# points_2 = np.vstack(downsampled_cloud.points)

segment = segment_point_cloud(points)


# normals = compute_normals(points)
# cloud.normals = o3d.utility.Vector3dVector(normals)
o3d.visualization.draw_geometries([segment[21]])

rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud,depth=6,width=0,linear_fit=False,n_threads=4)
avg_distance = np.mean(cloud.compute_nearest_neighbor_distance())
max_distance = np.max(cloud.compute_nearest_neighbor_distance())
min_distance = np.min(cloud.compute_nearest_neighbor_distance())

final = rec_mesh[0]
final = final.sample_points_poisson_disk(30000)
final.paint_uniform_color([0, 0, 1])
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
o3d.io.write_triangle_mesh("./data/abc.stl", rec_mesh)
o3d.visualization.draw_geometries([rec_mesh])
bunny = load_mesh('./data/abc.stl')

# bunny = examples.download_bunny()
# Define a camera position that shows the holes in the mesh
cpos = [(-0.2, -0.13, 0.12), (-0.015, 0.10, -0.0), (0.28, 0.26, 0.9)]

# Show mesh
bunny.plot(cpos=cpos)

# Generate a meshfix mesh ready for fixing and extract the holes
meshfix = mf.MeshFix(bunny)
holes = meshfix.extract_holes()


# Render the mesh and outline the holes
p = pv.Plotter()
p.add_mesh(bunny, color=True)
p.add_mesh(holes, color="r", line_width=4)
p.camera_position = cpos
p.enable_eye_dome_lighting()  # helps depth perception
p.show()


# Repair the mesh
meshfix.repair(verbose=True, joincomp=False,remove_smallest_components=False)

# Show the repaired mesh
meshfix.mesh.plot(cpos=cpos)

meshfix.mesh.save('finishMesh.stl')









