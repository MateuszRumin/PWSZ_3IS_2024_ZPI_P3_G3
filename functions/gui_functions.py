"""
###############################################################################################################
||                                                                                                           ||
||                                               Gui Functions                                               ||
||                                                                                                           ||
||This file contains minor functions from the gui and others that do not need to be split into separate files||
||                                                                                                           ||
###############################################################################################################
"""
import copy
import os
import vtk
import numpy as np
import pyvista as pv
import tempfile
import open3d as o3d
import threading
import time
from PyQt5.QtWidgets import QColorDialog
from functions import time_factory
import pandas as pd
from PIL import Image
from tkinter import filedialog
class GuiFunctions:
    #Declaration of global variables for GUI functions. They are probably not used outside this file
    use_distance = False
    distance = None
    use_area = False
    total_area = None
    label_area = None
    path = None
    roi = None
    roi_area = None
    #----------------------------------------------------------------------------------------------#

    #Function used to write down sampling values. Calls up object transformations
    def on_downSampling_size_change(self):
        value = self.voxel_size_slider.value()                  #Retrieving values from the slider
        self.settings.downSampling_size_slider_value = value    #Saving values to settings

        #Function calls
        self._apply_settings()
        #--------------

    #Changing the colour of the model
    def _change_model_color(self):
        color = QColorDialog.getColor() #Colour pick-up
        if color.isValid():
            #Colour assignment
            # pv.global_theme.font.color = color.name()
            self.colorTextActually.setStyleSheet(f'background: {color.name()}')
            self.plotter.set_color_cycler([color.name()])
            self.settings.object_color = color.name()
            #-----------------

            if self.create_mesh is not None:
                #Reloading mesh on plotter
                self.remove_mesh()
                self.add_mesh_to_plotter(self.create_mesh)


    #Changing the colour of the text
    def _change_text_color(self):
        color = QColorDialog.getColor() #Colour pick-up
        if color.isValid():
            #Colour assignment
            pv.global_theme.font.color = color.name()
            self.colorText.setStyleSheet(f'background: {color.name()}')
            #-----------------


    #Function that saves a scale value for setting. Calls up object transformations
    def _change_scale(self, key):
        #Increase or decrease the scale depending on the detected sign
        if key == "+":
            self.settings.scale_value = round((self.settings.scale_value + 0.1), 1)     #Saving values to settings
        elif key == "-":
            if self.settings.scale_value > 0.1:
                self.settings.scale_value = round((self.settings.scale_value - 0.1), 1) #Saving values to settings
        #-------------------------------------------------------------

        # Function calls
        self._apply_settings()
        #---------------

    #Function for determining distances
    def _distance_select(self):
        if self.checkDistance.isChecked():
            #Callback function called when a distance measurement is made
            def callback(a, b, distance):
                if distance >= 1000:
                    self.label = self.plotter.add_text(f'Distance: {float(distance / 1000):.2f} km', name='dist', position='lower_edge')
                elif distance >= 1:
                    self.label = self.plotter.add_text(f'Distance: {distance:.2f} m', name='dist', position='lower_edge')
                elif distance >= 0.01:
                    self.label = self.plotter.add_text(f'Distance: {distance * 100:.2f} cm', name='dist', position='lower_edge')
                else:
                    self.label = self.plotter.add_text(f'Distance: {distance * 1000:.2f} mm', name='dist', position='lower_edge')
                self.use_distance = True
            #------------------------------------------------------------

            #If no distance measurement widget has been added yet, add a distance measurement widget to the plotter
            if self.distance is None:
                self.distance = self.plotter.add_measurement_widget(callback)
            #------------------------------------------------------------------------------------------------------

            self.plotter.update()   #Update the plotter
        else:
            # If distance measurement was previously active
            if self.use_distance:
                self.distance.Off()                     #Turn off the distance measurement widget
                self.distance = None                    #Reset the distance measurement widget to None
                self.plotter.remove_actor(self.label)   #Remove the distance label from the plotter
                self.plotter.update()                   #Update the plotter
            #----------------------------------------------

    def _distance_mesh(self):

        if self.create_mesh is not None:

            if self.check_distance_mesh.isChecked():

                def callback(p):
                    self.show_loading_window()
                    thread = threading.Thread(target=lambda: callback_thread(p))
                    thread.start()

                def callback_thread(p):

                    indexes = p["vtkOriginalPointIds"]
                    distance = 0
                    for i in range(len(indexes) - 1):
                        a = indexes[i]
                        b = indexes[i + 1]

                        distance = distance + self.create_mesh.geodesic_distance(a, b)

                    #self.total_distance = self.plotter.add_text(f"Total distance: {distance} cm", name='dist', position='lower_edge')
                    self.addTotalDistanceToPlotterSignal.emit(distance)

                self.plotter.add_mesh(self.create_mesh)
                self.plotter.enable_geodesic_picking(callback=callback, show_message=True, font_size=18,
                                                color='red', point_size=6, line_width=4, tolerance=0.0001,
                                                show_path=True)

                self.plotter.update()

            else:
                self.plotter.remove_actor(self.total_distance)
                self.plotter.disable_picking()
                self.plotter.clear_actors()


    # Mesh area calculation function
    def _calculate_surface_area(self):
        if self.check_area.isChecked() and self.mesh_to_calculate_area:
            areas = []

            for i in range(len(self.mesh_to_calculate_area.v0)):
                v0 = self.mesh_to_calculate_area.v0[i]
                v1 = self.mesh_to_calculate_area.v1[i]
                v2 = self.mesh_to_calculate_area.v2[i]

                # Length of the sides of the triangle
                a = np.linalg.norm(v1 - v0)
                b = np.linalg.norm(v2 - v1)
                c = np.linalg.norm(v0 - v2)

                s = (a + b + c) / 2

                # Calculate triangle area
                area = np.sqrt(s * (s - a) * (s - b) * (s - c))
                areas.append(area)

            total_area = sum(areas)

            self.label_area = self.plotter.add_text(f'Area of the mesh: {total_area * 100:.2f} cm^2', name='area', position='lower_left')
            # self.label_area = self.plotter.add_text(f'Area of the mesh: {total_area}', name='area', position='lower_left')
            self.plotter.update()  # Update the plotter

        else:
            self.total_area = None            #Reset total area amount to None
            self.plotter.remove_actor(self.label_area)      #Remove the area label from the plotter
            self.plotter.update()           #Update the plotter


    #Function displaying object boundaries called by checkbox
    def _show_All_Bounds(self):
        if self.showAllBoundsCheck.isChecked():
            self.bounds_area = self.plotter.show_bounds(axes_ranges=[0, 100, 0, 100, 0, 100])
            self.plotter.update()
        else:
            print('Checkbox is not checked')
            self.plotter.remove_actor(self.bounds_area)

    #Background colour changing function
    def _change_background(self):
        color = QColorDialog.getColor() #Colour pick-up
        if color.isValid():
            #Colour assignment
            self.backgroundActually.setStyleSheet(f'background: {color.name()}')
            self.plotter.set_background(color.name())
            self.settings.background_plotter = color.name()
            #-----------------

    #Function that stores the value of an object's x-axis displacement in the setting. Calls up object transformations
    def move_in_x_axis(self, value):
        try:
            value = value.replace(',', '.')
        except:
            pass
        print(f"x", value)
        self.settings.object_move_in_x_direction = value


    #Function that stores the value of an object's y-axis displacement in the setting. Calls up object transformations
    def move_in_y_axis(self, value):
        try:
            value = value.replace(',', '.')
        except:
            pass
        print(f"y", value)
        self.settings.object_move_in_y_direction = value



    #Function that stores the value of an object's z-axis displacement in the setting. Calls up object transformations
    def move_in_z_axis(self, value):
        try:
            value = value.replace(',', '.')
        except:
            pass
        print(f"z", value)
        self.settings.object_move_in_z_direction = value



    #Function to store the value of rotation about the x-axis of an object in the settings. Calls up object transformations
    def _rotation_slider_x_change(self):
        value = self.rotation_x_slider.value()              #Retrieving values from the slider
        self.settings.rotate_slider_x_value = int(value)    #Saving values in the settings
        self._apply_settings()                              #Update gui

    # Function to store the value of rotation about the y-axis of an object in the settings. Calls up object transformations
    def _rotation_slider_y_change(self):
        value = self.rotation_y_slider.value()              #Retrieving values from the slider
        self.settings.rotate_slider_y_value = int(value)    #Saving values in the settings
        self._apply_settings()                              #Update gui

    # Function to store the value of rotation about the z-axis of an object in the settings. Calls up object transformations
    def _rotation_slider_z_change(self):
        value = self.rotation_z_slider.value()              #Retrieving values from the slider
        self.settings.rotate_slider_z_value = int(value)    #Saving values in the settings
        self._apply_settings()                              #Update gui


    def _transform_object(self):
        if self.cloud is not  None or self.create_mesh is not None:
            self.show_loading_window()
            thread = threading.Thread(target=self._transform_object_on_thread)
            thread.start()

    #A function that carries out the transformation of an object.
    def _transform_object_on_thread(self):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Geometry transformation'):
            if self.cloud is not None and self.display_cloud_checkbox.isChecked():
                #Logic equalizer
                if self.settings.transformation_logic_equalizer != [0, 0, 0, 0]:
                    if self.settings.transformation_logic_equalizer != [1, 0, 0, 0]:
                        #Overwrite backup and save changes in equalizer
                        #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                        # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                        #     self.create_mesh.save(self.create_mesh_backup.name)
                        self.overwriteBackupCloudSignal.emit(self.cloud)

                        self.settings.transformation_logic_equalizer = [1, 0, 0, 0]
                        self.settings.reset_smooth_values()
                        self.settings.reset_triangles_values()
                        self.settings.reset_subdivide_values()
                        self._apply_settings()


                if self.settings.transformation_logic_equalizer == [0, 0, 0, 0] or self.settings.transformation_logic_equalizer == [1, 0, 0, 0]:
                    try:
                        #self.cloud = copy.deepcopy(self.cloud_backup)   #Copy cloud form backup
                        self.removeActorSignal.emit("cloud")

                        self.cloud = pv.read(self.cloud_backup.name)

                        self.cloud = pv.PolyData(self.cloud.points)

                        #-----------Read values from settings-----------#
                        #Displacement
                        move_x = float(self.settings.object_move_in_x_direction)
                        move_y = float(self.settings.object_move_in_y_direction)
                        move_z = float(self.settings.object_move_in_z_direction)
                        #------------
                        #Rotation
                        rotation_x = self.settings.rotate_slider_x_value
                        rotation_y = self.settings.rotate_slider_y_value
                        rotation_z = self.settings.rotate_slider_z_value
                        #--------
                        #Scale
                        scale_value = self.settings.scale_value
                        #-----
                        #DownSampling
                        downSampling = self.settings.downSampling_size_slider_value / 1000
                        #-----------------------------------------------#

                        #-----------Cloud Transformations---------------#
                        #DownSampling
                        if downSampling > 0:
                            downSamplingCloud = self.cloud.clean(
                                point_merging=True,
                                merge_tol=downSampling,
                                lines_to_points=False,
                                polys_to_lines=False,
                                strips_to_polys=False,
                                inplace=False,
                                absolute=False,
                                progress_bar=False,
                            )
                            self.cloud = downSamplingCloud
                        #------------
                        #Displacement
                        translation_vector = np.array([move_x, move_y, move_z])
                        self.cloud.points += translation_vector
                        #------------
                        #Rotation
                        self.cloud = self.cloud.rotate_x(rotation_x, inplace=True, point=self.cloud.center)
                        self.cloud = self.cloud.rotate_y(rotation_y, inplace=True, point=self.cloud.center)
                        self.cloud = self.cloud.rotate_z(rotation_z, inplace=True, point=self.cloud.center)
                        #--------
                        #Scale
                        self.cloud.points *= scale_value
                        #-----------------------------------------------#

                        #Removing old cloud and adding new to plotter
                        #self.remove_cloud()
                        self.cloud = pv.PolyData(self.cloud.points)
                        #self.add_cloud_to_plotter(self.cloud)
                        self.addCloudSignal.emit(self.cloud)
                        self.settings.transformation_logic_equalizer = [1, 0, 0, 0]

                    except Exception as e:
                        print("[WARNING] Failed to transform cloud", e)

        if self.create_mesh is not None and (self.display_mesh_checkbox.isChecked() or self.display_triangles_checkbox.isChecked()):
            #Logic equalizer
            if self.settings.transformation_logic_equalizer != [0, 0, 0, 0]:
                if self.settings.transformation_logic_equalizer != [1, 0, 0, 0]:
                    #Overwrite backup and save changes in equalizer
                    #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                    # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                    #     self.create_mesh.save(self.create_mesh_backup.name)
                    self.overwriteBackupMeshSignal.emit(self.create_mesh)

                    self.settings.transformation_logic_equalizer = [1, 0, 0, 0]
                    self.settings.reset_smooth_values()
                    self.settings.reset_triangles_values()
                    self.settings.reset_subdivide_values()
                    self._apply_settings()
            #---------------

            if self.settings.transformation_logic_equalizer == [0, 0, 0, 0] or self.settings.transformation_logic_equalizer == [1, 0, 0, 0]:
                try:
                    #self.create_mesh = copy.deepcopy(self.create_mesh_backup)  #Copy mesh form backup
                    self.removeActorSignal.emit("mesh")
                    self.create_mesh = pv.read(self.create_mesh_backup.name)

                    # -----------Read values from settings-----------#
                    # Displacement
                    move_x = float(self.settings.object_move_in_x_direction)
                    move_y = float(self.settings.object_move_in_y_direction)
                    move_z = float(self.settings.object_move_in_z_direction)
                    # ------------
                    # Rotation
                    rotation_x = self.settings.rotate_slider_x_value
                    rotation_y = self.settings.rotate_slider_y_value
                    rotation_z = self.settings.rotate_slider_z_value
                    # --------
                    # Scale
                    scale_value = self.settings.scale_value
                    # -----------------------------------------------#

                    # ------------Mesh Transformations---------------#
                    #Displacement
                    translation_vector = np.array([move_x, move_y, move_z])
                    self.create_mesh.points += translation_vector
                    #------------
                    #Rotation
                    self.create_mesh = self.create_mesh.rotate_x(rotation_x, point=self.create_mesh.center)
                    self.create_mesh = self.create_mesh.rotate_y(rotation_y, point=self.create_mesh.center)
                    self.create_mesh = self.create_mesh.rotate_z(rotation_z, point=self.create_mesh.center)
                    #--------
                    #Scale
                    self.create_mesh.points *= scale_value
                    #------------------------------------------------#

                    #self.add_mesh_to_plotter(self.create_mesh)
                    self.addMeshSignal.emit(self.create_mesh)
                    self.settings.transformation_logic_equalizer = [1, 0, 0, 0]
                    #-------------------------------------------
                except Exception as e:
                    print("[WARNING] Failed to transform mesh", e)

    #Checkbox showing point cloud
    def _show_cloud_checked(self):
        if self.display_cloud_checkbox.isChecked():
            self.add_cloud_to_plotter(self.cloud)
        else:
            print('Checkbox is not checked')
            self.remove_cloud()

    # Checkbox showing normals
    def _show_normals_checked(self):
        if self.display_normals_checkbox.isChecked():
            if self.create_mesh is not None:
                self.create_mesh['vectors'] = self.create_mesh.face_normals

                # Creating normal arrows
                normals_arrows = self.create_mesh.glyph(
                    orient='vectors',
                    scale=False,
                    factor=0.009,
                )
                # ----------------------

                # Adding arrows to the plotter
                self.add_normals_to_plotter(normals_arrows)
                # ----------------------------
        else:
            print('Checkbox is not checked')
            self.remove_normals()

    # Checkbox showing mesh
    def _show_mesh_checked(self):
        if self.display_mesh_checkbox.isChecked():
            self.add_mesh_to_plotter(self.create_mesh)
        else:
            print('Checkbox is not checked')
            self.remove_mesh()

    def _show_triangles_checked(self):
        if self.display_triangles_checkbox.isChecked():
            self.add_mesh_with_triangles_to_plotter(self.create_mesh)
        else:
            print('Checkbox is not checked')
            self.remove_mesh_with_triangles()

    #Function activating the input field for the number of triangles
    def _enable_triangles_amount_input_field(self):
        if self.triangles_amount_checkbox.isChecked():
            self.settings.enable_triangles_amount_input_field = True
        else:
            self.settings.enable_triangles_amount_input_field = False

        #Function calls
        self._apply_settings()
        #--------------

    #Function called after changing the value in the field with the number of triangles
    def _triangles_amount_changed(self, value):
        self.settings.triangles_amount = value  #Entering values into the settings

    #Function called after changing models iteration slider
    def _model_iterations_slider_change(self):
        value = self.model_iterations_slider.value()    #Retrieving values from the slider
        self.settings.model_iterations_value = value    #Saving value to settings
        self._apply_settings()                          #Updating gui

    # Function called after changing models iteration slider
    def _prop_iteration_slider_changed(self):
        value = self.prop_iterations_slider.value()     # Retrieving values from the slider
        self.settings.prop_iterations_value = value     #Saving value to settings
        self._apply_settings()                          # Updating gui

    # Function called after changing models iteration slider
    def _number_of_parts_slider_changed(self):
        value = self.number_of_parts_slider.value()     # Retrieving values from the slider
        self.settings.number_of_parts_value = value     #Saving value to settings
        self._apply_settings()                          # Updating gui

    # Function called after changing models iteration slider
    def _min_points_on_path_slider_changed(self):
        value = self.min_points_on_path_slider.value()  # Retrieving values from the slider
        self.settings.min_points_on_path_value = value  #Saving value to settings
        self._apply_settings()                          # Updating gui

    # Function called after changing models iteration slider
    def curvature_threshold_slider_changed(self):
        value = self.curvature_treshold_slider.value()  # Retrieving values from the slider
        self.settings.curvature_threshold_value = value #Saving value to settings
        self._apply_settings()                          # Updating gui

    # Function called after changing neighbours slider
    def neighbours_slider_changed(self):
        value = self.neighbours_slider.value()  # Retrieving values from the slider
        self.settings.neighbours_value = value  # Saving value to settings
        self._apply_settings()                  # Updating gui

    #Function called after changing normalize checkbox
    def normalize_checkbox_changed(self):
        if self.normalize_checkbox.isChecked():
            self.settings.normalize_checkbox_value = True   #Setting normalize_checkbox_value in settings to True
        else:
            print('Checkbox is not checked')
            self.settings.normalize_checkbox_value = False  #Setting normalize_checkbox_value in settings to False


    def _calculate_area(self):
        self.plotter.update()  # Update the plotter

        #Checking if the mesh exists
        if self.create_mesh is not None:
            #Checking whether any other option is selected
            if self.calculate_comboBox.currentText() != 'None':
                #Calculate values for cells
                sized = self.create_mesh.compute_cell_sizes()
                sel_area = None
                #Displaying values for areas and giving them the appropriate unit
                if self.calculate_comboBox.currentText() == 'Areas':
                    MyTimer = time_factory.timer_factory()
                    with MyTimer('Calculate surface'):
                        #Removing existing label from plotter if exist
                        self.plotter.remove_actor(self.label_area)  # Remove the area label from the plotter
                        self.plotter.update()  # Update the plotter
                        #------------------------------------------------------------

                        #Displaying label
                        if (sized.area < 0.01):
                            self.label_area = self.plotter.add_text(f'Area of the mesh: {sized.area * 1000000:.2f} mm^2',
                                                                    name='area', position='lower_left')
                        elif (sized.area < 0.1):
                            self.label_area = self.plotter.add_text(f'Area of the mesh: {sized.area * 10000:.2f} cm^2',
                                                                    name='area', position='lower_left')
                        else:
                            self.label_area = self.plotter.add_text(f'Area of the mesh: {sized.area:.2f} m^2', name='area',
                                                                    position='lower_left')
                        #-----------------

                        self.plotter.update()  # Update the plotter
                #---------------------------------------------------
                # Displaying values for volume and giving them the appropriate unit
                elif self.calculate_comboBox.currentText() == 'Volume':
                    MyTimer = time_factory.timer_factory()
                    with MyTimer('Calculate volume'):
                        #Removing existing label from plotter if exist
                        self.plotter.remove_actor(self.label_area)  # Remove the area label from the plotter
                        self.plotter.update()  # Update the plotter
                        #---------------------------------------------

                        #Displaying label
                        if (sized.volume < 0.000001):
                            self.label_area = self.plotter.add_text(
                                f'Volume of the mesh: {sized.volume * 1000000000:.2f} mm^3', name='volume',
                                position='lower_left')
                        elif (sized.volume < 0.0001):
                            self.label_area = self.plotter.add_text(
                                f'Volume of the mesh: {sized.volume * 1000000:.2f} cm^3', name='volume',
                                position='lower_left')
                        elif (sized.volume < 0.01):
                            self.label_area = self.plotter.add_text(f'Volume of the mesh: {sized.volume * 1000:.2f} l',
                                                                    name='volume', position='lower_left')
                        else:
                            self.label_area = self.plotter.add_text(f'Volume of the mesh: {sized.volume:.2f} m^3',
                                                                    name='volume', position='lower_left')
                        #----------------
                        self.plotter.update()  # Update the plotter
                    # ---------------------------------------------------
                    # Displaying values for select area and giving them the appropriate unit
                elif self.calculate_comboBox.currentText() == "Select area":
                    # Disable selection
                    self.plotter.disable_picking()

                    if self.path is None:
                        # Removing existing label from plotter if exist
                        self.plotter.remove_actor(self.label_area)  # Remove the area label from the plotter
                        self.plotter.update()  # Update the plotter

                        def cBack(path):
                            # Set self.path data from enable_geodesic_picking
                            self.path = path

                        self.mesh_surf = self.create_mesh.extract_surface()
                        self.plotter.enable_geodesic_picking(cBack, tolerance=0.01, color='red')
                        self.plotter.reset_camera()
                        self.plotter.show()
                        self.plotter.update()  # Update the plotter

                    elif self.path is not None:
                        new_path = self.path
                        # Po wybraniu ścieżki, tworzymy maskę na podstawie wybranej ścieżki
                        # self.path = self.plotter.picked_geodesic
                        #self.path = self.path.extrude([0.008, 0.008, 0.008], capping=False)

                        mask = self.mesh_surf.select_enclosed_points(self.path.delaunay_2d(), check_surface=False,
                                                                     tolerance=0.15)
                        self.roi = mask.threshold(0.25, scalars="SelectedPoints")

                        vectors = mask.face_normals

                        mean_x = np.mean(vectors[:, 0])
                        mean_y = np.mean(vectors[:, 1])
                        mean_z = np.mean(vectors[:, 2])

                        print(f"x mean", mean_x)
                        print(f"y mean", mean_y)
                        print(f"z mean", mean_z)

                        self.path = new_path.extrude([mean_x, mean_y, mean_z], capping=False)
                        mesh_surf_2 = self.create_mesh.extract_surface()
                        mask = mesh_surf_2.select_enclosed_points(new_path.delaunay_2d(), check_surface=False)
                        self.roi = mask.threshold(0.25, scalars="SelectedPoints", method='upper')

                        print(f"PATH:     ", self.path)
                        print(f"MASK:     ", mask)
                        print(f"ROI:     ", self.roi)


                        # fast_plotter = pv.Plotter()
                        # fast_plotter.add_mesh(self.create_mesh, show_edges=True)
                        # fast_plotter.add_mesh(self.roi, show_edges=True, color="red")
                        # fast_plotter.add_mesh(self.path, show_edges=True, line_width=10, color="pink")
                        # fast_plotter.show()


                        self.plotter.update()  # Update the plotter

                        # Obliczanie powierzchni zaznaczonego obszaru
                        self.roi_area = self.roi.compute_cell_sizes().area
                        print(f"ROI AREA:     ", self.roi_area)

                        # Wyświetlanie obliczonej powierzchni
                        if (self.roi_area < 0.01):
                            self.label_area = self.plotter.add_text(
                                f'Area of the selected area: {self.roi_area * 1000000:.2f} mm^2',
                                name='area', position='lower_left')
                        elif (self.roi_area < 0.1):
                            self.label_area = self.plotter.add_text(
                                f'Area of the selected area: {self.roi_area * 10000:.2f} cm^2',
                                name='area', position='lower_left')
                        else:
                            self.label_area = self.plotter.add_text(
                                f'Area of the selected area: {self.roi_area:.2f} m^2',
                                name='area',
                                position='lower_left')

                        self.plotter.update()  # Update the plotter

                # ---------------------------------------------------
            else:
                #Clearing label from plotter
                self.plotter.remove_actor(self.label_area)  # Remove the area label from the plotter
                self.plotter.update()  # Update the plotter

    #Saving selected preset to settings
    def _normalize_preset_changed(self, text):
        if self.settings.change_normals_settings_manually == False:
            preset = next((item for item in self.settings.normalization_presets if item["name"] == text), None)
            if preset:
                self.settings.model_iterations_value = int(preset["model_iterations_value"])
                self.settings.prop_iterations_value = int(preset["prop_iterations_value"])
                self.settings.number_of_parts_value = int(preset["number_of_parts_value"])
                self.settings.min_points_on_path_value = int(preset["min_points_on_path_value"])
                self.settings.curvature_threshold_value = int(preset["curvature_threshold_value"])
                self.settings.neighbours_value = int(preset["neighbours_value"])
                self._apply_settings()

    #Activate normalize sliders
    def _change_values_manually_checkbox_changed(self):
        if self.change_values_manually_checkbox.isChecked():
            self.settings.change_normals_settings_manually = True
            self._apply_settings()
        else:
            self.settings.change_normals_settings_manually = False
            self._apply_settings()

    #Function called after change in smooth operations input field
    def _on_number_of_smooth_operations_value_changed(self, value):
        self.settings.number_of_smooth_iterations = value
        self._apply_settings()

    # Function called after change in subdivided operations input field
    def _on_number_of_subdevided_value_changed(self, value):
        self.settings.number_of_subdevide_iteration = value
        self._apply_settings()

    def _take_screen(self):
        try:
            file_path = filedialog.asksaveasfilename(
                initialdir="./screenshots",
                title="Zapisz zrzut ekranu",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                ]
            )
            if file_path:
                file_extension = os.path.splitext(file_path)[1]
                if file_extension == '.pdf':
                    self.plotter.save_graphic(file_path)
                if file_extension == '.png':
                    self.plotter.screenshot(file_path)
        except Exception as e:
            print("[WARNING] Failed to take a screenshot", e)

