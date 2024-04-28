class Settings:
    def __init__(self):
        self.file_path = None                               #Path to file
        self.downSampling_size_slider_value = 0             #DownSampling value
        self.scale_value = 1                                #Scale factor
        self.triangles_amount = 100                         #Triangles amount
        self.number_of_smooth_iterations = 1                #Smooth iterations
        self.number_of_subdevide_iteration = 1              #Subdevided iteractions
        self.transformation_logic_equalizer = [0, 0, 0, 0]  #Logic equalizer [transform, triangles, smooth, subdivide]

        #Cloud move values
        self.object_move_in_x_direction = 0
        self.object_move_in_y_direction = 0
        self.object_move_in_z_direction = 0

        #Cloud rotation values
        self.rotate_slider_x_value = 0
        self.rotate_slider_y_value = 0
        self.rotate_slider_z_value = 0

        #Export buttons
        self.enable_buttons_cloud = False
        self.enable_buttons_mesh = False
        self.normals_computed_for_origin = False
        self.changed_normals_computed = False

        #Triangles amount input field
        self.enable_triangles_amount_input_field = False

        #Normalize cloud
        self.normalize_checkbox_value = True

        #Change normals values manually
        self.change_normals_settings_manually = False

        #Enable create mesh button
        self.enable_create_mesh_button = False

        #Area checkbox
        self.enable_area_checkbox = False

        #Colors
        self.font_color_plotter = 'lightblue'
        self.background_plotter = 'gray'
        self.object_color = 'white'
        self.colorTextPlot = 'white'

        #Normalization sliders:
        self.model_iterations_value = 5
        self.prop_iterations_value = 3
        self.number_of_parts_value = 30
        self.min_points_on_path_value = 100
        self.curvature_threshold_value = 1
        self.neighbours_value = 50

        self.normalization_presets = [
            {"name": "Default", "cloud_size": 0, "model_iterations_value": 5, "prop_iterations_value": 3,
             "number_of_parts_value": 30, "min_points_on_path_value": 100, "curvature_threshold_value": 1,
             "neighbours_value": 50},
            {"name": "Small cloud", "cloud_size": 0, "model_iterations_value": 10, "prop_iterations_value": 3,
             "number_of_parts_value": 30, "min_points_on_path_value": 100, "curvature_threshold_value": 1,
             "neighbours_value": 50},
            {"name": "Large cloud", "cloud_size": 35000, "model_iterations_value": 15, "prop_iterations_value": 3,
             "number_of_parts_value": 30, "min_points_on_path_value": 100, "curvature_threshold_value": 1,
             "neighbours_value": 50},
        ]

    def reset_transformation_values(self):
        self.downSampling_size_slider_value = 0         #DownSampling value
        self.scale_value = 1                            #Scale factor

        # Cloud move values
        self.object_move_in_x_direction = 0
        self.object_move_in_y_direction = 0
        self.object_move_in_z_direction = 0

        # Cloud rotation values
        self.rotate_slider_x_value = 0
        self.rotate_slider_y_value = 0
        self.rotate_slider_z_value = 0

    def reset_smooth_values(self):
        self.number_of_smooth_iterations = 1            #Smooth iterations

    def reset_triangles_values(self):
        self.triangles_amount = 100                     #Triangles amount

    def reset_subdivide_values(self):
        self.number_of_subdevide_iteration = 1

