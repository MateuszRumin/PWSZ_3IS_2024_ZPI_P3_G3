"""
#####################################################################################################
||                                                                                                 ||
||                                         File Functions                                          ||
||                                                                                                 ||
||This file contains the functions responsible for reading and writing the point cloud and the mesh||
||                                                                                                 ||
||                                                                                                 ||
#####################################################################################################
"""

import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import QFileDialog
from pyntcloud import PyntCloud
from stl import mesh    #pip install numpy-stl

class FileFunctions:
    #Declaration of global variables for mesh and cloud available throughout the program
    cloud = None                            #Cloud
    cloud_backup = None                     #Cloud backup
    filePath = None                         #Variable for filepath
    cloud_geometry_container = None         #Cloud container, we refer to it when adding or removing a cloud
    cloud_normals_container = None          #Cloud normals container, we refer to it when adding or removing a cloud normals
    mesh_geometry_container = None          #Mesh container, we refer to it when adding or removing a mesh
    mesh_with_triangles_container = None    #Mesh with triangles container, we refer to it when adding or removing a mesh with triangles displayed
    mesh_to_calculate_area = None
    create_mesh = None                      #Mesh
    create_mesh_backup = None               #Mesh backup
    _origin_vectors = None                  #Original cloud vectors (overwritten after time)
    open3d_normalized_cloud = None          #Cloud in open3d with calculated normals
    #-----------------------------------------------------------------------------------

    #Function that takes the path to a file. It is called from the gui navigation bar
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "All Files (*);;LAS Files (*.las);;STL Files (*.stl);;LAZ Files (*.laz);;OBJ Files (*.obj);;PLY Files (*.ply)"
        self.filePath, _ = QFileDialog.getOpenFileName(self, "Choose file", "", filters, options=options)
        if self.filePath:
            self.settings.file_path = self.filePath     #Storing the file path in the application settings
            self.load(self.filePath)                    #Calling the function that loads the cloud/mesh from the selected path

    def load(self, path):
        self.remove_all_geometries_from_plotter()     #Clearing plotter

        #Clearing variables for clouds and meshes in case of reloading
        self.cloud = None
        self.cloud_backup = None
        self.create_mesh = None
        self.create_mesh_backup = None
        #-------------------------------------------------------------

        extension = path[-3:]   #Reading the extension to distinguish between cloud and mesh

        #Section loading a cloud or mesh from a specified path
        if extension == "ply" or extension == "pcd" or extension == "las" or extension == "laz":
            try:
                pyVistaCloud = PyntCloud.from_file(path)    #Loading the cloud using the pyntcloud library
                #----------------------------------------------------------
                #Conversion of the loaded cloud to PyVista. It eliminates errors that appear with some clouds.
                #It is responsible for loading some clouds with this intensity bar
                self.cloud = pyVistaCloud.to_instance("pyvista", mesh=False)
                #-----------------------------------------------------------
            except Exception as e:
                print("[WARNING] Failed to read points", path, e)
        else:
            try:
                self.create_mesh = pv.read(path)            #Loading a mesh from the selected location using pyvista's built-in functions
                self.mesh_to_calculate_area = mesh.Mesh.from_file(self.filePath)
                print("[Info] Successfully read", path)
            except Exception as e:
                print("[WARNING] Failed to read mesh", path, e)
        #------------------------------------------------------

        #Section adding the loaded cloud/mesh to the plotter
        if self.cloud is not None:
            #Cloud downsampling
            downSampling = self.settings.downSampling_size_slider_value / 1000
            downSamplingCloud = self.cloud.clean(
                point_merging=True,
                merge_tol=downSampling,
                lines_to_points=False,
                polys_to_lines=False,
                strips_to_polys=False,
                inplace=False,
                absolute=False,
                progress_bar=True,
            )
            self.cloud = downSamplingCloud
            #-----------------------------
            self.cloud_backup = self.cloud  #Creating cloud backup
            #-----------------------------
            self.add_cloud_to_plotter(self.cloud)      #Adding cloud to plotter
            #-----------------------------
        elif self.create_mesh is not None:
            self.create_mesh_backup = self.create_mesh  #Creating mesh backup
            #-----------------------------------------
            self.add_mesh_to_plotter(self.create_mesh)  #Adding mesh to plotter
            #-----------------------------------------
        #-------------------------------------------------------

    def read_cloud_from_mesh(self):
        if self.create_mesh is not None and self.cloud is None:
            self.cloud = pv.PolyData(self.create_mesh.points)

            # Cloud downsampling
            downSampling = self.settings.downSampling_size_slider_value / 1000
            downSamplingCloud = self.cloud.clean(
                point_merging=True,
                merge_tol=downSampling,
                lines_to_points=False,
                polys_to_lines=False,
                strips_to_polys=False,
                inplace=False,
                absolute=False,
                progress_bar=True,
            )
            self.cloud = downSamplingCloud
            # -----------------------------
            self.cloud_backup = self.cloud  # Creating cloud backup
            # -----------------------------
            self.add_cloud_to_plotter(self.cloud)  # Adding cloud to plotter
            # -----------------------------

    #Function that exports mesh to obj
    def _on_export_to_obj(self, mesh):
        #Selecting a location to save the file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "OBJ Files (*.obj);;All Files (*)"
        self.filePath, _ = QFileDialog.getSaveFileName(self, "Save OBJ File", "", filters, options=options)
        #-------------------------------------

        #Saving the mesh to a selected location
        if self.filePath:
            try:
                pv.save_meshio(self.filePath, self.create_mesh, file_format='obj')  #Export mesh using meshio
            except Exception as e:
                print("[WARNING] Failed to save mesh", e)
        #--------------------------------------

    # Function that exports mesh to stl
    def _on_export_to_stl(self, mesh):
        #Selecting a location to save the file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "STL Files (*.stl);;All Files (*)"
        self.filePath, _ = QFileDialog.getSaveFileName(self, "Save STL File", "", filters, options=options)
        #-------------------------------------

        #Saving the mesh to a selected location
        if self.filePath:
            try:
                self.create_mesh.save(self.filePath)
            except Exception as e:
                print("[WARNING] Failed to save mesh", e)
        #--------------------------------------

    # Function that exports cloud to ply
    def _on_export_to_ply(self):
        #Selecting a location to save the file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "PLY Files (*.ply);;All Files (*)"
        self.filePath, _ = QFileDialog.getSaveFileName(self, "Save PLY File", "", filters, options=options)
        #-------------------------------------

        # Saving the cloud to a selected location
        if self.filePath:
            try:
                points = self.cloud.points
                vertices = np.array(points)

                with open(self.filePath, 'w') as f:
                    f.write("ply\n")
                    f.write("format ascii 1.0\n")
                    f.write("element vertex %d\n" % len(vertices))
                    f.write("property float x\n")
                    f.write("property float y\n")
                    f.write("property float z\n")
                    f.write("end_header\n")
                    for vertex in vertices:
                        f.write("%f %f %f\n" % (vertex[0], vertex[1], vertex[2]))
            except Exception as e:
                print("[WARNING] Failed to save cloud", e)
        #-----------------------------------------

    #Functions for removing and addings elements to plotter
    def remove_all_geometries_from_plotter(self):
        #Removing all geometries from plotter
        try:
            self.plotter.remove_actor(self.cloud_geometry_container)
            print("cloud removed")
        except Exception as e:
            print("[WARNING] ", e)

        try:
            self.plotter.remove_actor(self.cloud_normals_container)
            print("normals removed")
        except Exception as e:
            print("[WARNING] ", e)

        try:
            self.plotter.remove_actor(self.mesh_geometry_container)
            print("mesh removed")
        except Exception as e:
            print("[WARNING] ", e)

        try:
            self.plotter.remove_actor(self.mesh_with_triangles_container)
            print("mesh with normals removed")
        except Exception as e:
            print("[WARNING] ", e)
        #------------------------------------

        #Setting all checkboxes to false
        self.display_cloud_checkbox.setChecked(False)
        self.display_normals_checkbox.setChecked(False)
        self.display_mesh_checkbox.setChecked(False)
        self.display_triangles_checkbox.setChecked(False)
        #-------------------------------

        #Clearing plotter containers
        self.cloud_geometry_container = None
        self.cloud_normals_container = None
        self.mesh_geometry_container = None
        self.mesh_with_triangles_container = None
        #---------------------------

        #Clearing checkbox for normals calculation
        self.settings.normals_computed_for_origin = False

    def remove_cloud(self):
        #Removing cloud from plotter
        try:
            self.plotter.remove_actor(self.cloud_geometry_container)
        except:
            pass
        #---------------------------

        #Setting checkbox to false
        self.display_cloud_checkbox.setChecked(False)

        #Clearing plotter container
        self.cloud_geometry_container = None

    def remove_normals(self):
        # Removing cloud from plotter
        try:
            self.plotter.remove_actor(self.cloud_normals_container)
        except:
            pass
        # ---------------------------

        # Setting checkbox to false
        self.display_normals_checkbox.setChecked(False)

        # Clearing plotter container
        self.cloud_normals_container = None

    def remove_mesh(self):
        # Removing cloud from plotter
        try:
            self.plotter.remove_actor(self.mesh_geometry_container)
        except:
            pass
        # ---------------------------

        # Setting checkbox to false
        self.display_mesh_checkbox.setChecked(False)

        # Clearing plotter container
        self.mesh_geometry_container = None

    def remove_mesh_with_triangles(self):
        # Removing cloud from plotter
        try:
            self.plotter.remove_actor(self.mesh_with_triangles_container)
        except:
            pass
        # ---------------------------

        # Setting checkbox to false
        self.display_triangles_checkbox.setChecked(False)

        # Clearing plotter container
        self.mesh_with_triangles_container = None


    def add_cloud_to_plotter(self, cloud):
        self.cloud_geometry_container = self.plotter.add_points(cloud, show_scalar_bar=False)  # Add points to plotter
        self.display_cloud_checkbox.setChecked(True)  # Check geometries checkbox
        self.plotter.update()  # Update the plotter to display the new mesh

        # Focus camera on object center
        center = cloud.center
        self.plotter.camera.SetFocalPoint(center[0], center[1], center[2])
        # -----------------------------

        # Enable cloud export buttons
        self.settings.enable_buttons_cloud = True
        self._apply_settings()
        # --------------------------

        self.plotter.show()

    def add_normals_to_plotter(self, normals):
        self.cloud_normals_container = self.plotter.add_mesh(normals, color='lightblue', show_scalar_bar=False)
        self.display_normals_checkbox.setChecked(True)


    def add_mesh_to_plotter(self, mesh):
        #Removing mesh with triangles if exist
        if self.display_triangles_checkbox.isChecked():
            self.remove_mesh_with_triangles()

        # Adding mesh to plotter
        self.mesh_geometry_container = self.plotter.add_mesh(mesh, show_edges=False, show_scalar_bar=False)
        self.display_mesh_checkbox.setChecked(True)
        # ----------------------

        # Enable mesh export buttons
        self.settings.enable_create_mesh_button = True
        self.settings.enable_buttons_mesh = True
        self._apply_settings()
        # ---------------------------

        self.plotter.show()

    def add_mesh_with_triangles_to_plotter(self, mesh):
        # Removing mesh if exist
        if self.display_mesh_checkbox.isChecked():
            self.remove_mesh()

        # Adding mesh to plotter
        self.mesh_with_triangles_container = self.plotter.add_mesh(mesh, show_edges=True, show_scalar_bar=False)
        self.display_triangles_checkbox.setChecked(True)
        # ----------------------

        # Enable mesh export buttons
        self.settings.enable_create_mesh_button = True
        self.settings.enable_buttons_mesh = True
        self._apply_settings()
        # ---------------------------

        self.plotter.show()

