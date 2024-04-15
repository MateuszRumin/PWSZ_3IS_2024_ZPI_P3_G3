"""
#################################################################################################
||                                                                                             ||
||                                      Normals Selection                                      ||
||                                                                                             ||
||This file contains the functions responsible for calculating and modifying the normal vectors||
||                                                                                             ||
#################################################################################################
"""
import copy
import threading
import numpy as np
import open3d as o3d
import pyvista as pv
from tqdm import tqdm

class NormalsSelection():
    #Declaration of global variables for normals selection
    cloud_for_indicates = None          #Cloud for open3d
    _selected_normals_cloud = None      #Trimmed vector cloud
    idx_table = []                      #Table of indices
    completed = 0                       #Number of indexes calculated
    origin_vectors_normalized = None    #Normal converted to open3d
    #-----------------------------------------------------

    #Vector calculation function
    def compute_vectors(self, mesh, point=np.array([0, 0, 0]), origin=True):
        #Vectors for the original cloud
        if origin == False:
            manualorigin = point
            vectors = (mesh.points - manualorigin) * -1
            vectors = vectors / np.linalg.norm(vectors, axis=1)[:, None]
            return vectors
        #------------------------------
        #Modified vectors
        elif origin == True:
            origin = mesh.center
            vectors = mesh.points - origin
            vectors = vectors / np.linalg.norm(vectors, axis=1)[:, None]
            return vectors
        #----------------

    #Function displaying normal vectors
    def display_cloud_normals(self):
        vectors = self.compute_vectors(self._selected_normals_cloud)    #Calculation of vectors from trimmed cloud
        vectors[0:5, :]                                                 #?

        self._selected_normals_cloud['vectors'] = vectors               #Assignment of vectors to the cloud
        sphere_center = np.array([0.0, 0.0, 0.0])                       #Determining the location of the editing sphere

        #Determination of arrows for vectors
        arrows = self._selected_normals_cloud.glyph(
            orient='vectors',
            scale=False,
            factor=0.009,
        )
        #-----------------------------------

        self.plotter.clear()    #Cleaning the plotter

        #Display of selected vectors and edit sphere
        self.cloud_normals_container = self.plotter.add_mesh(arrows, color='lightblue')
        self.plotter.add_sphere_widget(callback=self.callback, center=sphere_center, radius=0.01)
        #-------------------------------------------

    def callback(self, point):
        print(f"x:", round(point[0], 4))
        print(f"y", round(point[1], 4))
        print(f"z:", round(point[2], 4))

        #The condition checks whether the sphere has been moved from the point of addition.
        #The callback is called at the start of the program and without this condition it can cause problems
        if point[0] != 0 or point[1] != 0 or point[2] != 0:
            #Calculation of new vectors facing the sphere
            self.plotter.remove_actor(self.cloud_normals_container)
            vectors = self.compute_vectors(self._selected_normals_cloud, point, False)
            vectors[0:5, :]
            #--------------------------------------------

            #Adding the calculated vectors to the plotter
            self._selected_normals_cloud['vectors'] = vectors
            arrows = self._selected_normals_cloud.glyph(
                orient='vectors',
                scale=False,
                factor=0.009,
            )
            self.cloud_normals_container = self.plotter.add_mesh(arrows, color='lightblue')
            #--------------------------------------------

    def select_normals_area(self, picked):
        if isinstance(picked, pv.UnstructuredGrid):
            #Resetting the progress bar
            self.progressBar.setValue(0)
            self.completed = 0
            #--------------------------

            # Preparation and rounding to four decimal places of the marked points
            points_array = picked.GetPoints().GetData()
            print('-----------------------------------------------')
            num_points = points_array.GetNumberOfTuples()
            points = [
                [points_array.GetComponent(i, 0), points_array.GetComponent(i, 1), points_array.GetComponent(i, 2)]
                for i in range(num_points)]
            rounded_points = [tuple(round(coord, 4) for coord in point) for point in points]
            #---------------------------------------------------------------------

            # Calling a function that matches marked points to vertices on threads with a progress indicator from the tqdm library
            with tqdm(total=len(rounded_points), desc="Processing points") as pbar:
                threads = []
                for point in rounded_points:
                    #Calculation statement
                    thread = threading.Thread(target=self._calc_prefer_indicate, args=(point,))
                    #---------------------

                    #Running the calculations
                    thread.start()
                    threads.append(thread)
                    #------------------------

                    # Update the progress bar after each thread starts
                    pbar.update(1)
                    self.completed += 1
                    percent_complete = (self.completed / len(rounded_points)) * 100
                    self.progressBar.setValue(int(percent_complete))
                    #-------------------------------------------------

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                #---------------------------------

            #Display normals
            self._selected_normals_cloud = pv.PolyData(points)
            self.display_cloud_normals()
            #---------------

    #Function to mark areas for changing normal
    def select_points_for_normals(self):
        if self.cloud is not None:
            #Calculation of original vectors
            if self.settings.normals_computed_for_origin == False:
                self._origin_vectors = self.compute_vectors(self.cloud)
                self.settings.normals_computed_for_origin = True
            #-------------------------------

            #Cleaning the plotter
            self.plotter.clear()
            self.idx_table = []
            self.display_cloud_checkbox.setChecked(False)
            self.display_normals_checkbox.setChecked(False)
            self.display_mesh_checkbox.setChecked(False)
            self.display_triangles_checkbox.setChecked(False)
            #---------------------

            #Calling a function that marks points
            self.plotter.add_mesh(self.cloud)
            self.plotter.disable_picking()
            self.plotter.enable_cell_picking(callback=self.select_normals_area, style='surface',
                                             show_message=('Naciśnij R aby włąćzyć/wyłączyć zaznaczanie'))
            #-------------------------------------

    #Function to save changed normal to the cloud
    def save_normals(self):
        #Inclusion of modified normal in the cloud
        #An error occurs with the index of the cloud size value. NEEDS FIXING!
        i = 0
        for idx in self.idx_table:
            if i == self.completed:
                break
            elif idx == self.cloud.n_points:    #Temporary fixing the error
                print("?")
            elif i < len(self._selected_normals_cloud['vectors']):
                self._origin_vectors[idx] = self._selected_normals_cloud['vectors'][i]
                i += 1
            else:
                print(f"Index {i} is out of bounds for the vectors list.")
                break
        #-----------------------------------------

        #self._origin_vectors[0:5, :]

        #Calculation of arrows of normal vectors
        self.cloud['vectors'] = self._origin_vectors
        arrows = self.cloud.glyph(
            orient='vectors',
            scale=False,
            factor=0.009,
        )
        #---------------------------------------

        #Adding arrows to the plotter
        self.plotter.clear()    #This whole file is messed up and the plotter needs cleaning
        self.cloud_normals_container = self.plotter.add_mesh(arrows, color='lightblue')
        self.display_normals_checkbox.setChecked(True)
        #----------------------------

        #Calculation of normal vectors for open3d
        self.origin_vectors_normalized = self._origin_vectors / np.linalg.norm(self._origin_vectors, axis=1)[:, np.newaxis]
        #----------------------------------------

    def _calc_prefer_indicate(self, point):
        # In the absence of an existing cloud in open3d, it is calculated.
        # This fragment is called once by the soft start located in the file functions
        # In each subsequent case, only else is called.
        if self.cloud_for_indicates is None:
            # Conversion of pyvist cloud to open3d
            pyvista_points = self.cloud.points
            points_open3d = o3d.utility.Vector3dVector(pyvista_points)
            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = points_open3d
            # ------------------------------------

            # Maintaining the open3d cloud to reduce the number of calculations required
            self.cloud_for_indicates = copy.deepcopy(cloud_o3d)
            # --------------------------------------------------------------------------

            # Retrieve the previously saved open3d cloud to a local variable
            cloud = copy.deepcopy(self.cloud_for_indicates)
            # --------------------------------------------------------------

            # Point-to-vertex matching calculation
            cloud.points.append(np.asarray(point))
            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            self.idx_table.append(idx[-1])  # Saving the calculated index into an array
            # ------------------------------------
        else:
            # Retrieve the previously saved open3d cloud to a local variable
            cloud = copy.deepcopy(self.cloud_for_indicates)
            # --------------------------------------------------------------

            # Point-to-vertex matching calculation
            cloud.points.append(np.asarray(point))
            cloud_tree = o3d.geometry.KDTreeFlann(cloud)
            [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
            self.idx_table.append(idx[-1])  # Saving the calculated index into an array
            # ------------------------------------


