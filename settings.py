class Settings:
    def __init__(self):
        self.file_path = None                       #Path to file
        self.downSampling_size_slider_value = 1     #DownSampling value
        self.scale_value = 1                        #Scale factor
        self.triangles_amount = 100                 #Triangles amount

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

        #Enable create mesh button
        self.enable_create_mesh_button = False

        #Colors
        self.font_color_plotter = 'lightblue'
        self.background_plotter = 'gray'
        self.object_color = 'white'
        self.colorTextPlot = 'white'

        #Normalization sliders:
        self.model_iterations_value = 100
        self.prop_iterations_value = 10
        self.number_of_parts_value = 15
        self.min_points_on_path_value = 21
        self.curvature_threshold_value = 0
        self.neighbours_value = 30

