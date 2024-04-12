"""
################################################################################################
||                                                                                            ||
||                                       Mesh Selection                                       ||
||                                                                                            ||
||                    This file contains functions for selecting the mesh                     ||
||                                                                                            ||
################################################################################################
"""
import copy
import open3d as o3d
import pyvista as pv
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtWidgets
from pyvistaqt import QtInteractor


class MeshSelection():
    #Declaration of global variables for mesh and cloud available throughout the program
    indexes = []
    points = []
    #-----------------------------------------------------------------------------------

    #Function responsible for moving parts of the grid
    def move_sphere(self, point, i):
        idx = self.indexes[i]
        self.create_mesh.points[idx] = point


    #Function responsible for generating spheres for mesh editing
    def select_area(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            indexes = picked["orig_extract_id"]

            for selected_cell_index in indexes:
                selected_cell = self.create_mesh.get_cell(selected_cell_index)

                point_ids = selected_cell.point_ids
                points_coordinates = selected_cell.points

                self.points.append(points_coordinates[0])
                self.points.append(points_coordinates[1])
                self.points.append(points_coordinates[2])

                self.indexes.append(point_ids[0])
                self.indexes.append(point_ids[1])
                self.indexes.append(point_ids[2])


            self.plotter.add_sphere_widget(callback=self.move_sphere, center=self.points, radius=0.0010)
            #-------------------------------------


    #Function called from the gui which is responsible for selecting the editing area
    def _edit_mesh(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(callback=self.select_area, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

