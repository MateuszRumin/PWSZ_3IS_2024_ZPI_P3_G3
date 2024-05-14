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
import vtk

import pyvista as pv
import numpy as np
from tkinter import messagebox

from memory_profiler import profile
from functions import  time_factory
#import pyautogui


class CloudSelection():
    #Declaration of global variables for point indicates
    idx_points_table = []
    #---------------------------------------------------

    def showSelectedArea(self, picked):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Cloud selection'):
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
                    messagebox.showerror('Python Error', e)
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

    #Function to delete marked points
    def _delete_selected_points(self):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Delete selected points'):
            if self.idx_points_table is not None:
                try:
                    #Filtering the cloud by deleted points
                    indices_to_keep = np.setdiff1d(np.arange(self.cloud.n_points), self.idx_points_table)
                    cloud_filtered = self.cloud.extract_points(indices_to_keep)
                    self.cloud = cloud_filtered

                    with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
                        self.cloud.save(self.cloud_backup.name)
                        self.cleanup_handler.files_to_delete.append(self.cloud_backup.name)

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
                    messagebox.showerror('Python Error', e)
                finally:
                    self.idx_points_table = vtk.vtkTypeInt32Array()

    def _extract_selected_points(self):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Extract selected points'):
            if self.idx_points_table is not None:
                try:
                    #Filtering the cloud by deleted points
                    indices_to_keep = np.in1d(np.arange(self.cloud.n_points), self.idx_points_table)
                    cloud_filtered = self.cloud.extract_points(indices_to_keep)
                    self.cloud = cloud_filtered
                    #self.cloud_backup = copy.deepcopy(self.cloud)

                    with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
                        self.cloud.save(self.cloud_backup.name)
                        self.cleanup_handler.files_to_delete.append(self.cloud_backup.name)

                    #-------------------------------------
                    self._reset_plotter()
                    self.selected_points_value.setText("0")
                    #-----------------------------------

                    self.extract_selected_points_button.setEnabled(False)
                    self.plotter.update()
                except Exception as e:
                    print("[WARNING] Failed to extract points", e)
                    messagebox.showerror('Python Error', e)
                finally:
                    self.idx_points_table = vtk.vtkTypeInt32Array()
