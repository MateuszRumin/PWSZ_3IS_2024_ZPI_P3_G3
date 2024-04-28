"""
################################################################################################
||                                                                                            ||
||                                      Cloud Selection                                       ||
||                                                                                            ||
||              This file is responsible for selecting and deleting cloud points              ||
||                                                                                            ||
################################################################################################
"""
import copy
import tempfile

import pyvista as pv
import numpy as np
from memory_profiler import profile
#import pyautogui


class CloudSelection():
    #Declaration of global variables for point indicates
    idx_points_table = []
    #---------------------------------------------------

    def showSelectedArea(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            try:
                self.idx_points_table = []                                             #Resetting the index
                #-------------------------------------------------------
                self.idx_points_table = picked["orig_extract_id"]                      #Store indicates in idx_table
                self.selected_points_value.setText(str(len(self.idx_points_table)))    #Display in the gui of the number of marked points

                #plotter update and buttons activation
                self.plotter.update()
                self.delete_selected_points_button.setEnabled(True)
                self.extract_selected_points_button.setEnabled(True)

            except Exception as e:
                print("[WARNING] Failed to mark points", e)
            finally:
                del picked
        else:
            print("Something other than a cloud was marked.")

    #Function displaying a single marked point
    def showSelectedPoints(self, picked):
        self.idx_points_table = []                         # Resetting indicates table
        self.idx_points_table = picked["orig_extract_id"]  # Store indicates in idx_table
        self.selected_points_value.setText("1")
        print(self.idx_points_table[0])
        self.delete_selected_points_button.setEnabled(True)     #Activating delete points button

    #Marking function
    def _select_points(self):
        if self.cloud is not None and self.display_cloud_checkbox.isChecked():
            self.plotter.disable_picking()
            self.plotter.enable_cell_picking(self.showSelectedArea, style='surface',
                                             show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'), color='blue')

    #Function to mark a single point
    def _select_single_point(self):
        if self.cloud is not None and self.display_cloud_checkbox.isChecked():
            self.plotter.disable_picking()
            self.plotter.enable_point_picking(self.showSelectedPoints, style='surface',
                                              show_message=('Naciśnij P aby zaznaczyć punkt'), color='blue')

    #Function to delete marked points
    def _delete_selected_points(self):
        if self.idx_points_table is not None:
            try:
                #Filtering the cloud by deleted points
                indices_to_keep = np.setdiff1d(np.arange(self.cloud.n_points), self.idx_points_table)
                cloud_filtered = self.cloud.extract_points(indices_to_keep)
                self.cloud = cloud_filtered

                with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
                    self.cloud.save(self.cloud_backup.name)

                #self.cloud_backup = copy.deepcopy(self.cloud)
                #-------------------------------------

                #Re-loading the cloud to the plotter
                self._reset_plotter()
                self.selected_points_value.setText("0")
                #-----------------------------------

                self.delete_selected_points_button.setEnabled(False)    #Deactivating delete points button
                self.plotter.update()
            except Exception as e:
                print("[WARNING] Failed to delete points", e)
            finally:
                self.idx_points_table.clear()

    def _extract_selected_points(self):
        if self.idx_points_table is not None:
            try:
                #Filtering the cloud by deleted points
                indices_to_keep = np.in1d(np.arange(self.cloud.n_points), self.idx_points_table)
                cloud_filtered = self.cloud.extract_points(indices_to_keep)
                self.cloud = cloud_filtered
                #self.cloud_backup = copy.deepcopy(self.cloud)

                with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
                    self.cloud.save(self.cloud_backup.name)

                #-------------------------------------
                self._reset_plotter()
                self.selected_points_value.setText("0")
                #-----------------------------------

                self.extract_selected_points_button.setEnabled(False)
                self.plotter.update()
            except Exception as e:
                print("[WARNING] Failed to extract points", e)
            finally:
                self.idx_points_table.clear()
