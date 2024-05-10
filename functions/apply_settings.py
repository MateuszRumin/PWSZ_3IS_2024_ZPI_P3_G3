"""
#######################################################################################################################################
||                                                                                                                                   ||
||                                                          Apply Settings                                                           ||
||                                                                                                                                   ||
||                This file is responsible for implementing the values stored in the settings into the application.                  ||
||It is called at the start of the application, and it must be called every time we want to implement a value found in the settings. ||
||                                                                                                                                   ||
#######################################################################################################################################
"""
import pyvista as pv


class ApplySettings:
    def _apply_settings(self):
        # ---------------Enable values controller----------------------#
        if self.cloud is not None:
            self.settings.enable_buttons_cloud = True
        else:
            self.settings.enable_buttons_cloud = False
        if self.create_mesh is not None:
            self.settings.enable_buttons_mesh = True
        else:
            self.settings.enable_buttons_mesh = False
        #--------------------------------------------------------------#

        #---------------Settings of element values---------------------#
        self.scale_value_label.setText(str(self.settings.scale_value))                      #Scale value label
        self.triangles_amount_input_field.setText(str(self.settings.triangles_amount))      #Triangles amount input field
        self.move_x_value_field.setText(str(self.settings.object_move_in_x_direction))      # X displacement input field
        self.move_y_value_field.setText(str(self.settings.object_move_in_y_direction))      # Y displacement input field
        self.move_z_value_field.setText(str(self.settings.object_move_in_z_direction))      # Z displacement input field
        self.smooth_number_of_iterations_field.setText(str(self.settings.number_of_smooth_iterations))
        self.iterationSubdevide.setText(str(self.settings.number_of_subdevide_iteration))
        #--------------------------------------------------------------#

        #---------------------Enable objects---------------------------#
        #Export buttons
        self.export_to_ply.setEnabled(self.settings.enable_buttons_cloud)
        self.export_mesh_to_ply.setEnabled(self.settings.enable_buttons_mesh)
        self.export_to_obj.setEnabled(self.settings.enable_buttons_mesh)
        self.export_to_stl.setEnabled(self.settings.enable_buttons_mesh)
        #------------------
        #Create mesh button
        if self.settings.enable_buttons_cloud:
            self.create_mesh_button.setEnabled(True)
        else:
            self.create_mesh_button.setEnabled(False)
        #------------------
        #Calculate
        self.calculate_comboBox.setEnabled(self.settings.enable_buttons_mesh)
        self.calculate_area_button.setEnabled(self.settings.enable_buttons_mesh)
        #---------
        #Crop mesh button
        self.cropMeshButton.setEnabled(self.settings.enable_buttons_mesh)
        #----------------
        #Fix mesh button
        self.fix_mesh_button.setEnabled(self.settings.enable_buttons_mesh)
        #---------------
        #Reduce triangles button
        self.reduce_triangles_button.setEnabled(self.settings.enable_buttons_mesh)
        #-----------------------
        #Subdivide
        self.subdivideselect.setEnabled(self.settings.enable_buttons_mesh)
        self.iterationSubdevide.setEnabled(self.settings.enable_buttons_mesh)
        self.subdevideBtn.setEnabled(self.settings.enable_buttons_mesh)
        #---------
        #Smoothing
        self.smooth_button.setEnabled(self.settings.enable_buttons_mesh)
        self.smooth_number_of_iterations_field.setEnabled(self.settings.enable_buttons_mesh)
        #---------
        #Edit mesh
        self.cross_selection_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        self.edit_meshBtn.setEnabled(self.settings.enable_buttons_mesh)
        self.cropMeshButton.setEnabled(self.settings.enable_buttons_mesh)
        self.select_mesh_area_button.setEnabled(self.settings.enable_buttons_mesh)
        self.cropMeshSelected.setEnabled(self.settings.enable_buttons_mesh)
        self.extractMesh.setEnabled(self.settings.enable_buttons_mesh)
        #---------
        #Enable geometry transformation elements
        if self.cloud is not None or self.create_mesh is not None:
            self.scale_up_button.setEnabled(True)
            self.scale_down_button.setEnabled(True)
            self.move_x_value_field.setEnabled(True)
            self.move_y_value_field.setEnabled(True)
            self.move_z_value_field.setEnabled(True)
            self.rotation_x_slider.setEnabled(True)
            self.rotation_y_slider.setEnabled(True)
            self.rotation_z_slider.setEnabled(True)
            self.apply_transformation_values_button.setEnabled(True)
        else:
            self.scale_up_button.setEnabled(False)
            self.scale_down_button.setEnabled(False)
            self.move_x_value_field.setEnabled(False)
            self.move_y_value_field.setEnabled(False)
            self.move_z_value_field.setEnabled(False)
            self.rotation_x_slider.setEnabled(False)
            self.rotation_y_slider.setEnabled(False)
            self.rotation_z_slider.setEnabled(False)
            self.apply_transformation_values_button.setEnabled(False)
        #-----------------------
        #Enable display checkboxs
        self.display_cloud_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_normals_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        self.display_mesh_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        self.display_triangles_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        #------------------
        #Enable cloud manipulation buttons
        if self.cloud is not None:
            self.select_points_button.setEnabled(True)
            self.delete_points_button.setEnabled(True)
        else:
            self.select_points_button.setEnabled(False)
            self.delete_points_button.setEnabled(False)
        #---------------------------------

        #Enable all bounds checkbox
        if (self.settings.enable_buttons_cloud == True) or (self.settings.enable_buttons_mesh == True):
            self.showAllBoundsCheck.setEnabled(True)
            self.checkDistance.setEnabled(True)
        else:
            self.showAllBoundsCheck.setEnabled(False)
            self.checkDistance.setEnabled(False)
        self.check_distance_mesh.setEnabled(self.settings.enable_buttons_mesh)

        #Enable normalization stuff
        self.normalize_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.normalization_preset_combobox.setEnabled(self.settings.enable_buttons_cloud)
        self.change_values_manually_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        #--------------------------
        #--------------------------
        #Normalization checkbox
        self.normalize_checkbox.setChecked(self.settings.normalize_checkbox_value)
        #Enable triangles input field
        self.triangles_amount_input_field.setEnabled(self.settings.enable_triangles_amount_input_field)
        #--------------------------------------------------------------#

        #-----------------Theme and colors settings---------------------#
        pv.global_theme.font.color = self.settings.font_color_plotter                       #Font color
        self.plotter.set_background(self.settings.background_plotter)                       #Background color
        self.plotter.set_color_cycler([self.settings.object_color])                         #Object color
        self.colorTextActually.setStyleSheet(f'background: {self.settings.object_color}')   #Color text actually
        self.colorText.setStyleSheet(f'background: {self.settings.colorTextPlot}')          #Color text
        #---------------------------------------------------------------#

        #-----------------Set values to sliders and labels--------------#
        #Downsampling
        self.voxel_size_slider.setValue(self.settings.downSampling_size_slider_value)
        self.downsampling_value_label.setText(str(float(self.settings.downSampling_size_slider_value) / 1000))
        #------------
        #Rotation x slider
        self.rotatio_x_value_label.setText(str(self.settings.rotate_slider_x_value))
        # Rotation y slider
        self.rotation_y_value_label.setText(str(self.settings.rotate_slider_y_value))
        # Rotation z slider
        self.rotation_z_value_label.setText(str(self.settings.rotate_slider_z_value))
        #------------
        #Model iterations
        self.model_iterations_slider.setValue(self.settings.model_iterations_value)
        self.model_iterations_value_label.setText(str(self.settings.model_iterations_value))
        #----------------
        #Prop iterations
        self.prop_iterations_slider.setValue(self.settings.prop_iterations_value)
        self.prop_iterations_value_label.setText(str(self.settings.prop_iterations_value))
        #---------------
        #Number of parts
        self.number_of_parts_slider.setValue(self.settings.number_of_parts_value)
        self.number_of_part_value_label.setText(str(self.settings.number_of_parts_value))
        #---------------
        #Minimum points on path
        self.min_points_on_path_slider.setValue(self.settings.min_points_on_path_value)
        self.min_points_on_path_value_label.setText(str(self.settings.min_points_on_path_value))
        #----------------------
        #Curvature threshold
        self.curvature_treshold_slider.setValue(self.settings.curvature_threshold_value)
        self.curvature_threshold_value_label.setText(str(float(self.settings.curvature_threshold_value) / 100))
        #------------------
        #Neighbours
        self.neighbours_slider.setValue(self.settings.neighbours_value)
        self.neighbours_value_label.setText(str(self.settings.neighbours_value))
        #---------------------------------------------------------------#

        #Select normalization preset
        if self.cloud is not None:
            if self.normalization_preset_combobox.currentText() == '':
                for item in self.settings.normalization_presets:
                    if item["cloud_size"] < self.cloud.n_points:
                        self.normalization_preset_combobox.addItem(item['name'], item)


        #Change normals manually
        if self.settings.change_normals_settings_manually:
            self.model_iterations_slider.setEnabled(True)
            self.prop_iterations_slider.setEnabled(True)
            self.number_of_parts_slider.setEnabled(True)
            self.min_points_on_path_slider.setEnabled(True)
            self.curvature_treshold_slider.setEnabled(True)
            self.neighbours_slider.setEnabled(True)
            self.normalization_preset_combobox.setEnabled(False)
        else:
            self.model_iterations_slider.setEnabled(False)
            self.prop_iterations_slider.setEnabled(False)
            self.number_of_parts_slider.setEnabled(False)
            self.min_points_on_path_slider.setEnabled(False)
            self.curvature_treshold_slider.setEnabled(False)
            self.neighbours_slider.setEnabled(False)
            self.normalization_preset_combobox.setEnabled(True)


        # #Calculate area mesh checkbox toggle
        # if self.mesh_to_calculate_area:
        #     self.check_area.setEnabled(True)
        # else:
        #     self.check_area.setEnabled(False)
        # ---------------------------------------------------------------#