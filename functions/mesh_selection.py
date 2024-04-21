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
import os
import pyautogui
import vtk
from stl import mesh    #pip install numpy-stl


class MeshSelection():
    #Declaration of global variables for mesh and cloud available throughout the program
    indexes = []                            #Selected indexes table
    points = []                             #Selected points table
    #-----------------------------------------------------------------------------------

    #Function responsible for moving parts of the grid
    def move_sphere(self, point, i):
        idx = self.indexes[i]
        self.create_mesh.points[idx] = point

    #Function responsible for generating spheres for mesh editing
    def select_area(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            #Retrieving indexes of selected cells
            indexes = picked["original_cell_ids"]

            # Cleaning the plotter before marking an area.
            # Removes all unnecessary geometry causing errors.
            # Do not remove under any circumstances!
            self.plotter.clear_actors()
            pv.global_theme.restore_defaults()
            self.add_mesh_to_plotter(self.create_mesh)
            self.indexes = []
            self.points = []
            self.plotter.clear_sphere_widgets()
            #-------------------------------------------------

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

            #Reload mesh before adding spheres. Removes the glow of the selection area
            self.plotter.clear_actors()
            pyautogui.press('r')
            self.add_mesh_to_plotter(self.create_mesh)
            #-------------------------------------------------

            #Adding editing spheres to plotter
            self.plotter.add_sphere_widget(callback=self.move_sphere, center=self.points, radius=0.0010)
            #-------------------------------------

            #Activating checkboxes
            self.display_cloud_checkbox.setEnabled(True)
            self.display_normals_checkbox.setEnabled(True)
            self.display_mesh_checkbox.setEnabled(True)
            self.display_triangles_checkbox.setEnabled(True)


    def select_area_surface(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            self.indexes = []                                               #Resetting the index
            #-------------------------------------------------------
            self.indexes = picked["original_cell_ids"]                      #Store indicates in indexes
            self.selected_cells_value.setText(str(len(self.indexes)))       #Display in the gui of the number of marked points
        else:
            print("Something other than a mesh was marked.")
        print("cells selected")

        # Activating checkboxes
        self.display_cloud_checkbox.setEnabled(True)
        self.display_normals_checkbox.setEnabled(True)
        self.display_mesh_checkbox.setEnabled(True)
        self.display_triangles_checkbox.setEnabled(True)
        self.plotter.update()


    #Function called from the gui which is responsible for selecting the editing area
    def _edit_mesh(self):
        if self.create_mesh is not None and (self.display_mesh_checkbox.isChecked() or self.display_triangles_checkbox.isChecked()):
            # Prevent loading other geometry that does not support selection
            self.remove_all_geometries_from_plotter()
            self.add_mesh_to_plotter(self.create_mesh)
            self.display_cloud_checkbox.setEnabled(False)
            self.display_normals_checkbox.setEnabled(False)
            self.display_mesh_checkbox.setEnabled(False)
            self.display_triangles_checkbox.setEnabled(False)

            #Start picking
            self.plotter.disable_picking()
            self.plotter.enable_cell_picking(callback=self.select_area, through=False, style='surface',
                                             show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))

    def select_mesh_area(self):
        if self.create_mesh is not None and (self.display_mesh_checkbox.isChecked() or self.display_triangles_checkbox.isChecked()):
            # Prevent loading other geometry that does not support selection
            self.remove_all_geometries_from_plotter()
            self.add_mesh_to_plotter(self.create_mesh)
            self.display_cloud_checkbox.setEnabled(False)
            self.display_normals_checkbox.setEnabled(False)
            self.display_mesh_checkbox.setEnabled(False)
            self.display_triangles_checkbox.setEnabled(False)

            # Start picking
            self.plotter.disable_picking()
            self.plotter.enable_cell_picking(callback=self.select_area_surface, through=False, style='surface',
                                             show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))


    def crop_mesh_selected(self):
        if self.create_mesh is not None and (
                self.display_mesh_checkbox.isChecked() or self.display_triangles_checkbox.isChecked()):
            picked = self.plotter.picked_cells

            # crop mesh
            removed_mesh = self.create_mesh.remove_cells(picked["original_cell_ids"], inplace=False)
            self.create_mesh = removed_mesh

            self._reset_plotter()
            self.selected_cells_value.setText('0')

    def extract_mesh(self):
        if self.create_mesh is not None and (
                self.display_mesh_checkbox.isChecked() or self.display_triangles_checkbox.isChecked()):
            picked = self.plotter.picked_cells

            picked.save('./my2_selection.vtk')

            reader = vtk.vtkUnstructuredGridReader()
            reader.SetFileName("./my2_selection.vtk")  # Zastąp "input.vtk" ścieżką do twojego pliku

            surface_filter = vtk.vtkDataSetSurfaceFilter()
            surface_filter.SetInputConnection(reader.GetOutputPort())

            triangle_filter = vtk.vtkTriangleFilter()
            triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

            writer = vtk.vtkSTLWriter()
            writer.SetFileName("./my2_selection.stl")  # Zastąp "output.stl" ścieżką do wyjściowego pliku
            writer.SetInputConnection(triangle_filter.GetOutputPort())
            writer.Write()

            def load_mesh(file_path):
                if file_path.lower().endswith('.stl'):
                    mesh = pv.read(file_path)
                    os.remove(file_path)
                return mesh

            mesh_update = load_mesh('./my2_selection.stl')
            self.create_mesh = mesh_update

            self._reset_plotter()
            self.selected_cells_value.setText('0')


    #Trimming the mesh
    def crop_mesh_box(self):
        if self.create_mesh is not None:
            try:
                #Creating a new plotter with the possibility of trimming the grid
                clipped_plotter = pv.Plotter()
                _ = clipped_plotter.add_mesh_clip_box(self.create_mesh, color='white')
                clipped_plotter.show()
                #----------------------------------------------------------------

                #Replacement of old mesh with cropped mesh
                self.create_mesh = clipped_plotter.box_clipped_meshes[0]
                self.create_mesh.save('./siat333ka.vtk')
                print(self.create_mesh)
                reader = vtk.vtkUnstructuredGridReader()
                reader.SetFileName("./siat333ka.vtk")  # Zastąp "input.vtk" ścieżką do twojego pliku

                surface_filter = vtk.vtkDataSetSurfaceFilter()
                surface_filter.SetInputConnection(reader.GetOutputPort())

                triangle_filter = vtk.vtkTriangleFilter()
                triangle_filter.SetInputConnection(surface_filter.GetOutputPort())

                writer = vtk.vtkSTLWriter()
                writer.SetFileName("output.stl")  # Zastąp "output.stl" ścieżką do wyjściowego pliku
                writer.SetInputConnection(triangle_filter.GetOutputPort())
                writer.Write()

                print(f'writer ----------------------', writer)
                print(f'filter ----------------------', triangle_filter)

                def load_mesh(file_path):
                    if file_path.lower().endswith('.stl'):
                        mesh = pv.read(file_path)
                    return mesh

                mesh_update = load_mesh('./output.stl')

                self.create_mesh = mesh_update
                self.plotter.update()

                #-----------------------------------------


                self.remove_mesh()
                self.add_mesh_to_plotter(self.create_mesh)
                #-------------------------------------
            except Exception as e:
                print("[WARNING] Failed: ", e)

