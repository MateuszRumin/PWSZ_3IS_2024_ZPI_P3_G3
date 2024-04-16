"""
################################################################################################
||                                                                                            ||
||                                       Mesh Selection                                       ||
||                                                                                            ||
||                    This file contains functions for selecting the mesh                     ||
||                                                                                            ||
################################################################################################
"""
import pyvista as pv
import numpy as np
import pandas as pd
from stl import mesh    #pip install numpy-stl
import os



class MeshSelection():
    #Declaration of global variables for mesh and cloud available throughout the program
    indexes = []                            #Selected indexes table
    points = []                             #Selected points table
    #-----------------------------------------------------------------------------------

    #Function responsible for moving parts of the grid
    def move_sphere(self, point, i):
        idx = self.indexes[i]
        self.create_mesh.points[idx] = point

        # Zapisz zmodyfikowany mesh jako plik
        self.create_mesh.save('modified_mesh.stl')  # Załóżmy, że format pliku to STL

        # Otwórz nowo zapisany plik meshu i wczytaj go jako self.mesh_to_calculate_area
        self.mesh_to_calculate_area = mesh.Mesh.from_file('modified_mesh.stl')

        # Usuń plik tymczasowy
        os.remove('modified_mesh.stl')

        self._calculate_surface_area()  # Wywołanie funkcji do obliczenia powierzchni po przesunięciu punktu


    #Function responsible for generating spheres for mesh editing
    def select_area(self, picked):
        print(f"table: ", picked.array_names)
        if isinstance(picked, pv.UnstructuredGrid):
            indexes = picked["original_cell_ids"]

            self.plotter.clear_actors()
            self.add_mesh_to_plotter(self.create_mesh)

            for selected_cell_index in indexes:
                selected_cell = self.create_mesh.get_cell(selected_cell_index)  #Selecting a cell by id

                #Extracting information about point indexes and coordinates from the cell
                point_ids = selected_cell.point_ids
                points_coordinates = selected_cell.points
                #------------------------------------------------------------------------

                #The values returned by the cell are grouped into 3 elements.
                # So we need to break down these groups and add each element one at a time
                #ASSUMPTION THAT THE MESH CONSISTS OF TRIANGLES!
                self.points.append(points_coordinates[0])
                self.points.append(points_coordinates[1])
                self.points.append(points_coordinates[2])

                self.indexes.append(point_ids[0])
                self.indexes.append(point_ids[1])
                self.indexes.append(point_ids[2])
                #-------------------------------------------------------------------------


            #Deleting duplicates from selected points (REQUIRES TESTING!)
            big_array = np.array(self.points)
            df = pd.DataFrame(big_array)
            df_unique = df.drop_duplicates(keep='first')
            self.points = df_unique.to_numpy()
            #------------------------------------------------------------

            #Removing duplicates from selected indexes (REQUIRES TESTING!)
            unique_ids = list(dict.fromkeys(self.indexes))
            self.indexes = unique_ids
            #-------------------------------------------------------------

            self.plotter.clear_actors()
            self.add_mesh_to_plotter(self.create_mesh)

            #Adding editing spheres to plotter
            self.plotter.add_sphere_widget(callback=self.move_sphere, center=self.points, radius=0.0010)
            #-------------------------------------


    #Function called from the gui which is responsible for selecting the editing area
    def _edit_mesh(self):
        self.plotter.disable_picking()
        self.plotter.enable_cell_picking(callback=self.select_area, through=False, style='surface',
                                         show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

