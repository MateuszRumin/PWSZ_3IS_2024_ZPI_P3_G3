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
import pyntcloud
import pyvista as pv
import tempfile
import threading
from tkinter import messagebox


from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from pyntcloud import PyntCloud
from stl import mesh    #pip install numpy-stl
from memory_profiler import profile
from functions import time_factory



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
    total_distance = None
    #-----------------------------------------------------------------------------------

    #Function that takes the path to a file. It is called from the gui navigation bar
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "All Files (*);;LAS Files (*.las);;STL Files (*.stl);;LAZ Files (*.laz);;OBJ Files (*.obj);;PLY Files (*.ply)"
        self.filePath, _ = QFileDialog.getOpenFileName(self, "Choose file", "", filters, options=options)
        if self.filePath:
            self.settings.file_path = self.filePath     #Storing the file path in the application settings
            #self.load(self.filePath)                    #Calling the function that loads the cloud/mesh from the selected path
            self.show_loading_window()
            thread = threading.Thread(target=lambda: self.load(self.filePath))
            thread.start()


    #@profile
    def load(self, path):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Loading file'):
            cloud = None
            mesh = None
            self.clearBeforeLoadSignal.emit()

            extension = path[-3:]   #Reading the extension to distinguish between cloud and mesh

            if extension == "ply":
                file_type = self.identify_ply_file(path)
                if file_type == 'point_cloud':
                    extension = 'cloud'

            print(f"extension", extension)

            #Section loading a cloud or mesh from a specified path
            if extension == "pcd" or extension == "las" or extension == "laz" or extension == "cloud":
                try:
                    pyVistaCloud = PyntCloud.from_file(path)    #Loading the cloud using the pyntcloud library
                    #----------------------------------------------------------
                    #Conversion of the loaded cloud to PyVista. It eliminates errors that appear with some clouds.
                    #It is responsible for loading some clouds with this intensity bar
                    cloud = pyVistaCloud.to_instance("pyvista", mesh=False)
                    center = cloud.center

                    print(f"center", center)
                    cloud.points = cloud.points - center

                    #-----------------------------------------------------------
                except Exception as e:
                    print("[WARNING] Failed to read points", path, e)
                    messagebox.showerror('Python Error', e)
                    self.resetPlotterSignal.emit()
                finally:
                    del pyVistaCloud

            elif extension == "mesh":
                try:
                    mesh = pv.read(path)
                    mesh = mesh.triangulate()
                    print("[Info] Successfully read", path)
                except Exception as e:
                    print("[WARNING] Failed to read mesh", path, e)
                    messagebox.showerror('Python Error', e)
                    self.resetPlotterSignal.emit()
            else:
                try:
                    mesh = pv.read(path)            #Loading a mesh from the selected location using pyvista's built-in functions
                    #self.mesh_to_calculate_area = mesh.Mesh.from_file(self.filePath)
                    mesh = mesh.triangulate()
                    print("[Info] Successfully read", path)
                except Exception as e:
                    print("[WARNING] Failed to read mesh", path, e)
                    messagebox.showerror('Python Error', e)
                    self.resetPlotterSignal.emit()
            #------------------------------------------------------

            #Section adding the loaded cloud/mesh to the plotter
            if cloud is not None:
                #Cloud downsampling
                if self.settings.downSampling_size_slider_value > 0:
                    downSampling = self.settings.downSampling_size_slider_value / 1000
                    downSamplingCloud = cloud.clean(
                        point_merging=True,
                        merge_tol=downSampling,
                        lines_to_points=False,
                        polys_to_lines=False,
                        strips_to_polys=False,
                        inplace=False,
                        absolute=False,
                        progress_bar=True,
                    )
                    cloud = pv.PolyData(downSamplingCloud.points)
                #-----------------------------
                #self.cloud_backup = self.cloud  #Creating cloud backup

                # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
                #     self.cloud.save(self.cloud_backup.name)
                self.assignCloudSignal.emit(cloud)
                self.overwriteBackupCloudSignal.emit(cloud)
                #-----------------------------
                #self.add_cloud_to_plotter(self.cloud)      #Adding cloud to plotter
                self.addCloudSignal.emit(cloud)
                #-----------------------------
            elif mesh is not None:
                #self.create_mesh_backup = self.create_mesh  #Creating mesh backup
                # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                #     self.create_mesh.save(self.create_mesh_backup.name)
                self.assignMeshSignal.emit(mesh)
                self.overwriteBackupMeshSignal.emit(mesh)
                #-----------------------------------------
                #self.add_mesh_to_plotter(self.create_mesh)  #Adding mesh to plotter
                self.addMeshSignal.emit(mesh)
                #-----------------------------------------
            #-------------------------------------------------------

    def read_cloud_from_mesh(self):
        if self.create_mesh is not None and self.cloud is None:
            self.show_loading_window()
            thread = threading.Thread(target=self.read_cloud_from_mesh_thread)
            thread.start()

    def read_cloud_from_mesh_thread(self):
        if self.create_mesh is not None and self.cloud is None:
            cloud = pv.PolyData(self.create_mesh.points)

            # Cloud downsampling
            if self.settings.downSampling_size_slider_value > 0:
                downSampling = self.settings.downSampling_size_slider_value / 1000
                downSamplingCloud = cloud.clean(
                    point_merging=True,
                    merge_tol=downSampling,
                    lines_to_points=False,
                    polys_to_lines=False,
                    strips_to_polys=False,
                    inplace=False,
                    absolute=False,
                    progress_bar=True,
                )
                cloud = pv.PolyData(downSamplingCloud.points)
            # -----------------------------
            #self.cloud_backup = self.cloud  # Creating cloud backup
            self.assignCloudSignal.emit(cloud)
            # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.cloud_backup:
            #     self.cloud.save(self.cloud_backup.name)
            self.overwriteBackupCloudSignal.emit(cloud)

            # -----------------------------
            #self.add_cloud_to_plotter(self.cloud)  # Adding cloud to plotter
            self.addCloudSignal.emit(cloud)
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
                messagebox.showerror('Python Error', e)
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
                messagebox.showerror('Python Error', e)
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
                messagebox.showerror('Python Error', e)
        #-----------------------------------------

    def _on_export_mesh_to_ply(self):
        # Selecting a location to save the file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "PLY Files (*.ply);;All Files (*)"
        self.filePath, _ = QFileDialog.getSaveFileName(self, "Save PLY File", "", filters, options=options)
        # -------------------------------------

        # Saving the cloud to a selected location
        if self.filePath:
            try:
                self.create_mesh.save(self.filePath)
                print("Mesh was successively saved")
            except Exception as e:
                print("[WARNING] Failed to save mesh", e)
                messagebox.showerror('Python Error', e)
        # -----------------------------------------

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

        try:
            self.plotter.clear_sphere_widgets()
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

    def _reset_plotter(self):
        self.plotter.clear_actors()
        self.plotter.clear_sphere_widgets()

        self._remove_and_add_plotter_to_field_in_app()

        if self.display_cloud_checkbox.isChecked():
            self.add_cloud_to_plotter(self.cloud)
            center = self.cloud.center
            self.plotter.camera.SetFocalPoint(center[0], center[1], center[2])

        if self.display_normals_checkbox.isChecked():
            self.display_normals_checkbox.setChecked(False)
            self.cloud_normals_container = None

        if self.display_mesh_checkbox.isChecked():
            self.add_mesh_to_plotter(self.create_mesh)
            center = self.create_mesh.center
            self.plotter.camera.SetFocalPoint(center[0], center[1], center[2])

        if self.display_triangles_checkbox.isChecked():
            self.add_mesh_with_triangles_to_plotter(self.create_mesh)
            center = self.create_mesh.center
            self.plotter.camera.SetFocalPoint(center[0], center[1], center[2])

        self.check_distance_mesh.setChecked(False)
        self.showAllBoundsCheck.setChecked(False)
        self.checkDistance.setChecked(False)
        self.calculate_comboBox.setCurrentText('None')
        self.selected_points_value.setText('0')
        # self.subdivideselect.setCurrentText('None')
        # self.iterationSubdevide.setText('1')
        # self.smooth_number_of_iterations_field.setText('1')
        self.normalize_checkbox.setChecked(True)
        self.change_values_manually_checkbox.setChecked(False)
        if self.cloud is not None:
            self.normalization_preset_combobox.setCurrentText('Default')

        self._apply_settings()





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

        try:
            self.plotter.clear_sphere_widgets()
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

        try:
            self.plotter.clear_sphere_widgets()
        except:
            pass
        # ---------------------------

        # Setting checkbox to false
        self.display_triangles_checkbox.setChecked(False)

        # Clearing plotter container
        self.mesh_with_triangles_container = None


    def add_cloud_to_plotter(self, cloud):
        self.cloud_geometry_container = self.plotter.add_points(cloud, show_scalar_bar=False, render_points_as_spheres=True, color=self.settings.object_color)  # Add points to plotter
        self.display_cloud_checkbox.setChecked(True)  # Check geometries checkbox
        self.plotter.update()  # Update the plotter to display the new mesh

        # Focus camera on object center
        #center = cloud.center
        #self.plotter.camera.SetFocalPoint(center[0], center[1], center[2])
        # -----------------------------

        # Enable cloud export buttons
        self.settings.enable_buttons_cloud = True
        #self._apply_settings()
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
        self.mesh_geometry_container = self.plotter.add_mesh(mesh, show_edges=False, show_scalar_bar=False, color=self.settings.object_color)
        self.display_mesh_checkbox.setChecked(True)
        # ----------------------

        # Focus camera on object center
        #center = mesh.center
        #self.plotter.camera.SetFocalPoint(center[0], center[1], center[2])
        # -----------------------------

        # Enable mesh export buttons
        self.settings.enable_create_mesh_button = True
        self.settings.enable_buttons_mesh = True
        #self._apply_settings()
        # ---------------------------

        self.plotter.show()

    def add_mesh_with_triangles_to_plotter(self, mesh):
        # Removing mesh if exist
        if self.display_mesh_checkbox.isChecked():
            self.remove_mesh()

        # Adding mesh to plotter
        self.mesh_with_triangles_container = self.plotter.add_mesh(mesh, show_edges=True, show_scalar_bar=False, color=self.settings.object_color)
        self.display_triangles_checkbox.setChecked(True)
        # ----------------------

        # Enable mesh export buttons
        self.settings.enable_create_mesh_button = True
        self.settings.enable_buttons_mesh = True
        #self._apply_settings()
        # ---------------------------

        self.plotter.show()

    def identify_ply_file(self, path):
        try:
            cloud = pyntcloud.PyntCloud.from_file(path)
            if not cloud.mesh.empty:
                return 'mesh'
        except Exception:
            return "point_cloud"
        return "unknown"
