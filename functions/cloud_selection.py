"""
################################################################################################
||                                                                                            ||
||                                      Cloud Selection                                       ||
||                                                                                            ||
||              This file is responsible for selecting and deleting cloud points              ||
||                                                                                            ||
################################################################################################
"""
import pyvista as pv
import numpy as np


class CloudSelection():
    #Declaration of global variables for point indicates
    idx_table = []
    #---------------------------------------------------

    def showSelectedArea(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            self.idx_table = []                                             #Resetting the index
            #-------------------------------------------------------
            self.idx_table = picked["orig_extract_id"]                      #Store indicates in idx_table
            self.selected_points_value.setText(str(len(self.idx_table)))    #Display in the gui of the number of marked points
        else:
            print("Something other than a cloud was marked.")
        print("points selected")
        self.plotter.update()
        self.delete_selected_points_button.setEnabled(True)


    #Function displaying a single marked point
    def showSelectedPoints(self, picked):
        self.idx_table = []                         # Resetting indicates table
        self.idx_table = picked["orig_extract_id"]  # Store indicates in idx_table
        self.selected_points_value.setText("1")
        print(self.idx_table[0])
        self.delete_selected_points_button.setEnabled(True)     #Activating delete points button

    #Marking function
    def _select_points(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(self.showSelectedArea, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    #Function to mark a single point
    def _select_single_point(self):
        self.plotter.disable_picking()
        self.plotter.enable_point_picking(self.showSelectedPoints, style='surface',
                                          show_message=('Naciśnij P aby zaznaczyć punkt'))

    #Function to delete marked points
    def _delete_selected_points(self):
        if self.idx_table is not None:
            #Filtering the cloud by deleted points
            indices_to_keep = np.setdiff1d(np.arange(self.cloud.n_points), self.idx_table)
            cloud_filtered = self.cloud.extract_points(indices_to_keep)
            self.cloud = cloud_filtered
            #-------------------------------------

            #Re-loading the cloud to the plotter
            self.plotter.remove_actor(self.cloud_geometry_container)
            self.cloud_geometry_container = self.plotter.add_points(self.cloud)
            self.selected_points_value.setText("0")
            #-----------------------------------

            self.delete_selected_points_button.setEnabled(False)    #Deactivating delete points button


