import laspy
import open3d as o3d
import numpy as np
import open3d.visualization as vis
import os
import random
import tkinter as tk
import math

def point_clouds(file):
    # Wczytywanie pliku las
    las_file = laspy.read(f"{file}")

    # Tworzenie chmury z pliku
    points = np.vstack([las_file.x, las_file.y, las_file.z]).T
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)

    # Obliczanie normalnych
    cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    def make_mesh(o3dvis):
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud)
        mesh.paint_uniform_color((1, 1, 1))
        mesh.compute_vertex_normals()

        o3dvis.add_geometry({"name": RESULT_NAME, "geometry": mesh})
        o3dvis.show_geometry(SOURCE_NAME, False)

    def toggle_result(o3dvis):
        truth_vis = o3dvis.get_geometry(TRUTH_NAME).is_visible
        o3dvis.show_geometry(TRUTH_NAME, not truth_vis)
        o3dvis.show_geometry(RESULT_NAME, truth_vis)

    def edit_point(o3dvis):
        o3d.visualization.draw_geometries_with_editing([cloud])

    SOURCE_NAME = "Source"
    RESULT_NAME = "Result (Poisson reconstruction)"
    TRUTH_NAME = "Ground truth"

    vis.draw([{
        "name": SOURCE_NAME,
        "geometry": cloud
    }, {
        "name": TRUTH_NAME,
        "geometry": cloud,
        "is_visible": False
    }],
             actions=[("Create Mesh", make_mesh),
                      ("Toggle truth/result", toggle_result),
                      ("Edit Points", edit_point)])

