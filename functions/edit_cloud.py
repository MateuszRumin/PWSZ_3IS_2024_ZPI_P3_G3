import numpy as np

from libraries import *

class PointEditor:
    def _edit_points(self):
        self.manual_registration()


    def manual_registration(self):
        self.source = self.cloud
        source_points = self.pick_points(self.source)
        print(source_points)

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
        print(vis.get_cropped_geometry())
        return vis.get_picked_points()