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
        #---------------Settings of element values---------------------#
        self.scale_value_label.setText(str(self.settings.scale_value))                      #Scale value label
        self.triangles_amount_input_field.setText(str(self.settings.triangles_amount))      #Triangles amount input field
        #--------------------------------------------------------------#

        #---------------------Enable objects---------------------------#
        #Export buttons
        self.export_to_ply.setEnabled(self.settings.enable_buttons_cloud)
        self.export_to_obj.setEnabled(self.settings.enable_buttons_mesh)
        self.export_to_stl.setEnabled(self.settings.enable_buttons_mesh)
        #------------------
        #Create mesh button
        if self.settings.enable_buttons_cloud or self.settings.enable_create_mesh_button:
            self.create_mesh_button.setEnabled(True)
        else:
            self.create_mesh_button.setEnabled(False)
        #------------------
        #Crop mesh button
        self.cropMeshButton.setEnabled(self.settings.enable_buttons_mesh)
        #----------------
        #Change normals button
        self.change_normals_button.setEnabled(self.settings.enable_buttons_cloud)
        #---------------------
        #Save normals button
        self.save_normals_button.setEnabled(self.settings.enable_buttons_cloud)
        #-------------------
        #Fix mesh button
        self.fix_mesh_button.setEnabled(self.settings.enable_buttons_mesh)
        #---------------
        #Enable rotation sliders
        if self.cloud is not None or self.create_mesh is not None:
            self.rotation_x_slider.setEnabled(True)
            self.rotation_y_slider.setEnabled(True)
            self.rotation_z_slider.setEnabled(True)
        #-----------------------
        #Enable display checkboxs
        self.display_cloud_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_normals_checkbox.setEnabled(self.settings.enable_buttons_cloud)
        self.display_mesh_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        self.display_triangles_checkbox.setEnabled(self.settings.enable_buttons_mesh)
        #------------------
        #Enable all bounds checkbox
        if (self.settings.enable_buttons_cloud == True) or (self.settings.enable_buttons_mesh == True):
            self.showAllBoundsCheck.setEnabled(True)
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
        #Curvature treshold
        self.curvature_treshold_slider.setValue(self.settings.curvature_threshold_value)
        self.curvature_threshold_value_label.setText(str(float(self.settings.curvature_threshold_value) / 100))
        #------------------
        #Neighbours
        self.neighbours_slider.setValue(self.settings.neighbours_value)
        self.neighbours_value_label.setText(str(self.settings.neighbours_value))
        #---------------------------------------------------------------#

        #Calculate area mesh checkbox toggle
        if self.mesh_to_calculate_area:
            self.check_area.setEnabled(True)
        else:
            self.check_area.setEnabled(False)
        # ---------------------------------------------------------------#