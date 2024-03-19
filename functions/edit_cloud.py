import numpy as np

from libraries import *


class PointEditor:
    def _edit_points(self):
        self.manual_registration()

    def manual_registration(self):
        self.source = self.cloud
        source_points = self.pick_points(self.source)
        print(source_points)   # [] with no. point
        self.source = self.delete_pick_points(self.source, source_points)
        print(f"SOURCE: ", self.source)

        # Display visualization cloud without remove points
        # source_points = self.pick_points(self.source)
        # print(source_points)  # [] with no. point

    def pick_points(self, pcd):
        print(
            "1) Please pick at least three correspondences using [shift + left click]"
        )
        print("   Press [shift + right click] to undo point picking")
        print("2) After picking points, press 'Q' to close the window")
        vis = o3d.visualization.VisualizerWithEditing()
        vis.create_window()
        vis.add_geometry(pcd)
        vis.run()  # user picks points
        vis.destroy_window()
        print("---------------------------------------------")
        print(vis.get_cropped_geometry())   # PointCloud with ... points.
        return vis.get_picked_points()

    def delete_pick_points(self, pcd, picked_points):
        # List number of pick points to index
        indices_to_delete = picked_points

        # Delete picks points from org cloud
        pcd.points = o3d.utility.Vector3dVector(
            np.delete(np.asarray(pcd.points), indices_to_delete, axis=0)
        )
        if pcd.colors:
            pcd.colors = o3d.utility.Vector3dVector(
                np.delete(np.asarray(pcd.colors), indices_to_delete, axis=0)
            )
        print("Deleted picked points from the original point cloud.")
        return pcd
