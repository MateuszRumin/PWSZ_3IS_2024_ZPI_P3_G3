from libraries import *
import open3d.visualization as vis


class CreateGuiMesh:

    def point_clouds(self, cloud):
        def make_mesh(o3dvis):
            radii = [0.005, 0.01, 0.02, 0.04]
            rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                cloud, o3d.utility.DoubleVector(radii))

            pcd = rec_mesh.sample_points_poisson_disk(5000)
            pcd.normals = o3d.utility.Vector3dVector(np.zeros(
                (1, 3)))  # invalidate existing normals

            # o3d.visualization.draw_geometries([pcd, rec_mesh])

            o3dvis.add_geometry({"name": self.RESULT_NAME, "geometry": rec_mesh})
            o3dvis.show_geometry(self.SOURCE_NAME, False)

        self.SOURCE_NAME = "Source"
        self.RESULT_NAME = "Result (Poisson reconstruction)"
        self.TRUTH_NAME = "Ground truth"

        vis.draw([{
            "name": self.SOURCE_NAME,
            "geometry": cloud
        }, {
            "name": self.TRUTH_NAME,
            "geometry": cloud,
            "is_visible": False
        }])

        make_mesh(vis.Visualizer())

    def __init__(self):
        pass  # Add any initialization if needed


# Example usage:
# mesh_creator = CreateGuiMesh()
# mesh_creator.point_clouds(cloud)
