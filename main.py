# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# Copyright (c) 2018-2023 www.open3d.org
# SPDX-License-Identifier: MIT
# ----------------------------------------------------------------------------

#imports
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

from libraries import *
from functions import apply_settings
from functions import file_functions
from functions import gui_functions
from functions import on_layout
from functions import mesh_creator
from functions import edit_cloud
from settings import Settings
from functions.mesh_creator import MeshCreator
from functions.edit_cloud import PointEditor

isMacOS = (platform.system() == "Darwin")

class AppWindow(apply_settings.ApplySettings, file_functions.FileFunctions, gui_functions.GuiFunctions, on_layout.OnLayout, mesh_creator.MeshCreator, edit_cloud.PointEditor):
    MENU_OPEN = 1
    MENU_QUIT = 3
    MENU_SHOW_SETTINGS = 11
    MENU_ABOUT = 21

    def __init__(self, width, height):
        self.settings = Settings()
        resource_path = gui.Application.instance.resource_path
        self.settings.new_ibl_name = resource_path + "/" + AppWindow.DEFAULT_IBL

        self.window = gui.Application.instance.create_window(
            "Open3D", width, height)
        w = self.window  # to make the code more concise
        w.set_on_close(self.on_window_close)

        # 3D widget
        self._scene = gui.SceneWidget()
        self._scene.scene = rendering.Open3DScene(w.renderer)
        self._scene.set_on_sun_direction_changed(self._on_sun_dir)


        # ---- Settings panel ----
        # Rather than specifying sizes in pixels, which may vary in size based
        # on the monitor, especially on macOS which has 220 dpi monitors, use
        # the em-size. This way sizings will be proportional to the font size,
        # which will create a more visually consistent size across platforms.
        em = w.theme.font_size
        separation_height = int(round(0.5 * em))

        # Widgets are laid out in layouts: gui.Horiz, gui.Vert,
        # gui.CollapsableVert, and gui.VGrid. By nesting the layouts we can
        # achieve complex designs. Usually we use a vertical layout as the
        # topmost widget, since widgets tend to be organized from top to bottom.
        # Within that, we usually have a series of horizontal layouts for each
        # row. All layouts take a spacing parameter, which is the spacing
        # between items in the widget, and a margins parameter, which specifies
        # the spacing of the left, top, right, bottom margins. (This acts like
        # the 'padding' property in CSS.)
        self._settings_panel = gui.Vert(
            0, gui.Margins(0.25 * em, 0.25 * em, 0.25 * em, 0.25 * em))


        #--------------------------------------------------------------------
        # Creating CollapsableVert for view controls
        view_ctrls = gui.CollapsableVert("View controls", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))

        #Arcball button
        self._arcball_button = gui.Button("Arcball")
        self._arcball_button.horizontal_padding_em = 0.5
        self._arcball_button.vertical_padding_em = 0
        self._arcball_button.set_on_clicked(self._set_mouse_mode_rotate)

        #Fly button
        self._fly_button = gui.Button("Fly")
        self._fly_button.horizontal_padding_em = 0.5
        self._fly_button.vertical_padding_em = 0
        self._fly_button.set_on_clicked(self._set_mouse_mode_fly)

        #Model button
        self._model_button = gui.Button("Model")
        self._model_button.horizontal_padding_em = 0.5
        self._model_button.vertical_padding_em = 0
        self._model_button.set_on_clicked(self._set_mouse_mode_model)

        #Environment button
        self._ibl_button = gui.Button("Environment")
        self._ibl_button.horizontal_padding_em = 0.5
        self._ibl_button.vertical_padding_em = 0
        self._ibl_button.set_on_clicked(self._set_mouse_mode_ibl)

        #Label
        view_ctrls.add_child(gui.Label("Mouse controls"))

        # We want two rows of buttons, so make two horizontal layouts. We also
        # want the buttons centered, which we can do be putting a stretch item
        # as the first and last item. Stretch items take up as much space as
        # possible, and since there are two, they will each take half the extra
        # space, thus centering the buttons.
        h = gui.Horiz(0.25 * em)  # row 1
        h.add_stretch()
        h.add_child(self._arcball_button)
        h.add_child(self._fly_button)
        h.add_child(self._model_button)
        h.add_stretch()

        #Adding first row to CollapsableVert
        view_ctrls.add_child(h)

        h = gui.Horiz(0.25 * em)  # row 2
        h.add_stretch()
        h.add_child(self._ibl_button)
        h.add_stretch()

        # Adding second row to CollapsableVert
        view_ctrls.add_child(h)

        #Color picker
        self._bg_color = gui.ColorEdit()
        self._bg_color.set_on_value_changed(self._on_bg_color)
        grid = gui.VGrid(2, 0.25 * em)
        grid.add_child(gui.Label("BG Color"))
        grid.add_child(self._bg_color)
        view_ctrls.add_child(grid)

        #Model axes
        self._show_axes = gui.Checkbox("Show axes")
        self._show_axes.set_on_checked(self._on_show_axes)
        view_ctrls.add_fixed(separation_height)
        view_ctrls.add_child(self._show_axes)

        #Adding view controls to settings panel
        self._profiles = gui.Combobox()
        self._settings_panel.add_fixed(separation_height)
        self._settings_panel.add_child(view_ctrls)

        #?
        self._ibl_map = gui.Combobox()
        for ibl in glob.glob(gui.Application.instance.resource_path +
                             "/*_ibl.ktx"):
            self._ibl_map.add_item(os.path.basename(ibl[:-8]))


        #----------------------------------------------------------------
        #Material settings CollapsableVert
        material_settings = gui.CollapsableVert("Material settings", 0,
                                                gui.Margins(em, 0, 0, 0))
        #Shader
        self._shader = gui.Combobox()
        self._shader.add_item(AppWindow.MATERIAL_NAMES[0])
        self._shader.add_item(AppWindow.MATERIAL_NAMES[1])
        self._shader.add_item(AppWindow.MATERIAL_NAMES[2])
        self._shader.add_item(AppWindow.MATERIAL_NAMES[3])
        self._shader.set_on_selection_changed(self._on_shader)

        #Material prefab
        self._material_prefab = gui.Combobox()
        for prefab_name in sorted(Settings.PREFAB.keys()):
            self._material_prefab.add_item(prefab_name)
        self._material_prefab.selected_text = Settings.DEFAULT_MATERIAL_NAME
        self._material_prefab.set_on_selection_changed(self._on_material_prefab)

        #Material color
        self._material_color = gui.ColorEdit()
        self._material_color.set_on_value_changed(self._on_material_color)

        #Point size
        self._point_size = gui.Slider(gui.Slider.INT)
        self._point_size.set_limits(1, 10)
        self._point_size.set_on_value_changed(self._on_point_size)

        #Grid layout
        grid = gui.VGrid(2, 0.25 * em)

        #Grid type
        grid.add_child(gui.Label("Type"))
        grid.add_child(self._shader)

        #Grid material
        grid.add_child(gui.Label("Material"))
        grid.add_child(self._material_prefab)

        #Grid color
        grid.add_child(gui.Label("Color"))
        grid.add_child(self._material_color)

        #Grid point size
        grid.add_child(gui.Label("Point size"))
        grid.add_child(self._point_size)
        material_settings.add_child(grid)

        #Adding elements to settings panel
        self._settings_panel.add_fixed(separation_height)
        self._settings_panel.add_child(material_settings)

        #-------------------------------------------------------

        complement_ctrls = gui.CollapsableVert("Complements", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))

        #Slider1
        self._complement_slider_1 = gui.Slider(gui.Slider.INT)
        self._complement_slider_1.set_limits(1, 100)
        self._complement_slider_1.set_on_value_changed(self._on_complement_slider_1_change)

        # scale button+
        self.scale_plus_button = gui.Button("+")
        self.scale_plus_button.set_on_clicked(lambda: self._change_scale("+"))
        self.scale_plus_button.horizontal_padding_em = 0.5
        self.scale_plus_button.vertical_padding_em = 0

        # scale button-
        self.scale_minus_button = gui.Button("-")
        self.scale_minus_button.set_on_clicked(lambda: self._change_scale("-"))
        self.scale_minus_button.horizontal_padding_em = 0.5
        self.scale_minus_button.vertical_padding_em = 0

        #Scale value
        self.scale_value_label = gui.Label(str(self.settings.scale_value))


        # Slider3
        self._complement_slider_3 = gui.Slider(gui.Slider.INT)
        self._complement_slider_3.set_limits(1, 100)
        self._complement_slider_3.set_on_value_changed(self._on_complement_slider_3_change)

        sliders_layout = gui.Horiz(0.25 * em)  # row 1
        sliders_layout.add_child(gui.Label("Voxel Size: "))
        sliders_layout.add_child(self._complement_slider_1)
        sliders_layout.add_stretch()

        # Adding first row to CollapsableVert
        complement_ctrls.add_child(sliders_layout)

        sliders_layout = gui.Horiz(0.25 * em)  # row 2
        sliders_layout.add_child(gui.Label("Scale: "))
        sliders_layout.add_stretch()
        sliders_layout.add_child(self.scale_value_label)

        sliders_layout.add_stretch()
        sliders_layout.add_child(self.scale_plus_button)
        sliders_layout.add_child(self.scale_minus_button)
        sliders_layout.add_stretch()

        # Adding second row to CollapsableVert
        complement_ctrls.add_child(sliders_layout)

        sliders_layout = gui.Horiz(0.25 * em)  # row 3
        sliders_layout.add_child(gui.Label("Slider 3: "))
        sliders_layout.add_child(self._complement_slider_3)
        sliders_layout.add_stretch()

        # Adding third row to CollapsableVert
        complement_ctrls.add_child(sliders_layout)

        #Adding sliders to CollapsableVert
        self._settings_panel.add_child(complement_ctrls)

        #-------------------------------------------------------
        #Creating CollapsableVert for mesh controls
        mesh_ctrls = gui.CollapsableVert("Convert to mesh", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))

        #Create grid for points input field
        points_grid = gui.VGrid(4, 0.25 * em)

        points_grid.add_child(gui.Label("Points (m^2):"))

        self._points_number = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._points_number.set_limits(1, 1000)
        self._points_number.set_value(100)
        self._points_number.enabled = self.settings.points_enabled


        #Checkbox to enable points change
        points_grid.add_child(gui.Label(""))
        self._points_checkbox = gui.Checkbox("")
        self._points_checkbox.set_on_checked(self._on_points_checkbox)
        points_grid.add_child(self._points_number)
        points_grid.add_child(self._points_checkbox)

        #Add elements to collapse
        mesh_ctrls.add_child(points_grid)

        #Max points on object
        max_points_layout = gui.Horiz(0.25 * em)  # row 1
        max_points_layout.add_child(gui.Label("Max points on object:"))
        max_points_layout.add_stretch()
        mesh_ctrls.add_child(max_points_layout)

        #Max points on object number box
        max_points_layout = gui.Horiz(0.25 * em)  # row 2
        self._max_points_numer = gui.NumberEdit(gui.NumberEdit.Type.INT)
        self._max_points_numer.set_limits(1, 100000)
        self._max_points_numer.set_value(10000)
        self._max_points_numer.enabled = self.settings.max_points_enabled
        max_points_layout.add_child(self._max_points_numer)

        # Max points on object checbox
        self._max_points_checkbox = gui.Checkbox("")
        self._max_points_checkbox.set_on_checked(self._on_max_points_checkbox)
        max_points_layout.add_child(self._max_points_checkbox)


        max_points_layout.add_stretch()
        mesh_ctrls.add_child(max_points_layout)

        #Normalize all points
        normalize_points_layout = gui.Horiz(0.25 * em)
        normalize_points_layout.add_child(gui.Label("Normalize all points:"))

        self._normalize_points_checkbox = gui.Checkbox("")
        self._normalize_points_checkbox.set_on_checked(self._on_normalize_points_checkbox)
        normalize_points_layout.add_child(self._normalize_points_checkbox)
        mesh_ctrls.add_child(normalize_points_layout)


        #Button layout
        button_layout = gui.Horiz(0.25 * em)

        #Create mesh button
        self.make_mesh_button = gui.Button("Create mesh")
        self.make_mesh_button.set_on_clicked(lambda: self._make_mesh(self.settings.file_path, self._points_number.int_value, self._max_points_numer.int_value, self.settings.normalize_all_points, self.cloud, self._complement_slider_1.int_value))
        self.make_mesh_button.horizontal_padding_em = 0.5
        self.make_mesh_button.vertical_padding_em = 0
        button_layout.add_child(self.make_mesh_button)


        #Edit mesh button
        self.edit_points_button = gui.Button("Edit points")
        self.edit_points_button.set_on_clicked(self._edit_points)
        self.edit_points_button.horizontal_padding_em = 0.5
        self.edit_points_button.vertical_padding_em = 0
        button_layout.add_child(self.edit_points_button)

        #Adding elements to CollapsableVert
        mesh_ctrls.add_child(button_layout)

        #Adding CollapsableVert to settings panel
        self._settings_panel.add_child(mesh_ctrls)

        # -------------------------------------------------------
        # Creating CollapsableVert for scene controls
        scene_ctrls = gui.CollapsableVert("Scene geometries", 0.25 * em,
                                         gui.Margins(em, 0, 0, 0))

        # Selection of the displayed model
        self.geometry_models_tree = gui.TreeView()
        self.root = self.geometry_models_tree.get_root_item()
        scene_ctrls.add_child(self.geometry_models_tree)

        # Adding CollapsableVert to settings panel
        self._settings_panel.add_child(scene_ctrls)


        #----------------------------------------------------------
        move_obj_ctrls = gui.CollapsableVert("Move object", 0.25 * em,
                                               gui.Margins(em, 0, 0, 0))


        #x+
        self.x_plus_button = gui.Button("+")
        self.x_plus_button.set_on_clicked(lambda: self.move_in_x_axis("+"))
        self.x_plus_button.horizontal_padding_em = 0.5
        self.x_plus_button.vertical_padding_em = 0

        # x-
        self.x_minus_button = gui.Button("-")
        self.x_minus_button.set_on_clicked(lambda: self.move_in_x_axis("-"))
        self.x_minus_button.horizontal_padding_em = 0.5
        self.x_minus_button.vertical_padding_em = 0

        # y+
        self.y_plus_button = gui.Button("+")
        self.y_plus_button.set_on_clicked(lambda: self.move_in_y_axis("+"))
        self.y_plus_button.horizontal_padding_em = 0.5
        self.y_plus_button.vertical_padding_em = 0

        # y-
        self.y_minus_button = gui.Button("-")
        self.y_minus_button.set_on_clicked(lambda: self.move_in_y_axis("-"))
        self.y_minus_button.horizontal_padding_em = 0.5
        self.y_minus_button.vertical_padding_em = 0

        # z+
        self.z_plus_button = gui.Button("+")
        self.z_plus_button.set_on_clicked(lambda: self.move_in_z_axis("+"))
        self.z_plus_button.horizontal_padding_em = 0.5
        self.z_plus_button.vertical_padding_em = 0

        # z-
        self.z_minus_button = gui.Button("-")
        self.z_minus_button.set_on_clicked(lambda: self.move_in_z_axis("-"))
        self.z_minus_button.horizontal_padding_em = 0.5
        self.z_minus_button.vertical_padding_em = 0

        t = gui.Horiz(0.25 * em)  # row 1
        t.add_stretch()
        t.add_child(gui.Label("x"))
        t.add_child(self.x_plus_button)
        t.add_child(self.x_minus_button)
        t.add_stretch()

        # Adding first row to CollapsableVert
        move_obj_ctrls.add_child(t)

        t = gui.Horiz(0.25 * em)  # row 2
        t.add_stretch()
        t.add_child(gui.Label("y"))
        t.add_child(self.y_plus_button)
        t.add_child(self.y_minus_button)
        t.add_stretch()

        # Adding second row to CollapsableVert
        move_obj_ctrls.add_child(t)

        t = gui.Horiz(0.25 * em)  # row 3
        t.add_stretch()
        t.add_child(gui.Label("z"))
        t.add_child(self.z_plus_button)
        t.add_child(self.z_minus_button)
        t.add_stretch()

        # Adding third row to CollapsableVert
        move_obj_ctrls.add_child(t)

        #Rotation sliders
        move_obj_ctrls.add_child(gui.Label("Rotation Sliders"))

        # x slider
        self._rotation_slider_x = gui.Slider(gui.Slider.INT)
        self._rotation_slider_x.set_limits(0, 360)
        self._rotation_slider_x.set_on_value_changed(self._rotation_slider_x_change)

        # y slider
        self._rotation_slider_y = gui.Slider(gui.Slider.INT)
        self._rotation_slider_y.set_limits(0, 360)
        self._rotation_slider_y.set_on_value_changed(self._rotation_slider_y_change)

        # z slider
        self._rotation_slider_z = gui.Slider(gui.Slider.INT)
        self._rotation_slider_z.set_limits(0, 360)
        self._rotation_slider_z.set_on_value_changed(self._rotation_slider_z_change)

        rotation_sliders = gui.Horiz(0.25 * em)  # row 1
        rotation_sliders.add_stretch()
        rotation_sliders.add_child(gui.Label("x"))
        rotation_sliders.add_child(self._rotation_slider_x)
        rotation_sliders.add_stretch()

        move_obj_ctrls.add_child(rotation_sliders)

        rotation_sliders = gui.Horiz(0.25 * em)  # row 2
        rotation_sliders.add_stretch()
        rotation_sliders.add_child(gui.Label("y"))
        rotation_sliders.add_child(self._rotation_slider_y)
        rotation_sliders.add_stretch()

        move_obj_ctrls.add_child(rotation_sliders)

        rotation_sliders = gui.Horiz(0.25 * em)  # row 3
        rotation_sliders.add_stretch()
        rotation_sliders.add_child(gui.Label("z"))
        rotation_sliders.add_child(self._rotation_slider_z)
        rotation_sliders.add_stretch()

        move_obj_ctrls.add_child(rotation_sliders)


        self._settings_panel.add_child(move_obj_ctrls)

        # ----------------------------------------------------------
        export_ctrls = gui.CollapsableVert("Exports", 0.25 * em,
                                             gui.Margins(em, 0, 0, 0))

        # Export buttons
        export_buttons_layout = gui.Horiz(0.25 * em)

        # Export to OBJ
        self.export_to_obj_button = gui.Button("OBJ/file")
        self.export_to_obj_button.set_on_clicked(lambda: self._on_export_to_obj(self.create_mesh))
        self.export_to_obj_button.horizontal_padding_em = 0.5
        self.export_to_obj_button.vertical_padding_em = 0
        export_buttons_layout.add_child(self.export_to_obj_button)

        # Export to STL
        self.export_to_stl_button = gui.Button("STL/file")
        self.export_to_stl_button.set_on_clicked(lambda: self._on_export_to_stl(self.create_mesh))
        self.export_to_stl_button.horizontal_padding_em = 0.5
        self.export_to_stl_button.vertical_padding_em = 0
        export_buttons_layout.add_child(self.export_to_stl_button)

        export_ctrls.add_child(export_buttons_layout)

        # -----------------------------------------------------

        # Export buttons cloud
        export_buttons_cloud_layout = gui.Horiz(0.25 * em)

        # Export to PLY
        self.export_to_ply_button = gui.Button("PLY")
        self.export_to_ply_button.set_on_clicked(self._on_export_to_ply)
        self.export_to_ply_button.horizontal_padding_em = 0.5
        self.export_to_ply_button.vertical_padding_em = 0
        export_buttons_cloud_layout.add_child(self.export_to_ply_button)

        # Export to PCD
        self.export_to_pcd_button = gui.Button("PCD")
        self.export_to_pcd_button.set_on_clicked(self._on_export_to_pcd)
        self.export_to_pcd_button.horizontal_padding_em = 0.5
        self.export_to_pcd_button.vertical_padding_em = 0
        export_buttons_cloud_layout.add_child(self.export_to_pcd_button)

        export_ctrls.add_child(export_buttons_cloud_layout)

        self._settings_panel.add_child(export_ctrls)

        # ----

        #Set ColapsableVert to close
        view_ctrls.set_is_open(False)
        material_settings.set_is_open(False)
        complement_ctrls.set_is_open(False)
        mesh_ctrls.set_is_open(False)
        scene_ctrls.set_is_open(False)
        move_obj_ctrls.set_is_open(False)
        export_ctrls.set_is_open(False)

        # Normally our user interface can be children of all one layout (usually
        # a vertical layout), which is then the only child of the window. In our
        # case we want the scene to take up all the space and the settings panel
        # to go above it. We can do this custom layout by providing an on_layout
        # callback. The on_layout callback should set the frame
        # (position + size) of every child correctly. After the callback is
        # done the window will layout the grandchildren.
        w.set_on_layout(self._on_layout)
        w.add_child(self._scene)
        w.add_child(self._settings_panel)

        # ---- Menu ----
        # The menu is global (because the macOS menu is global), so only create
        # it once, no matter how many windows are created
        if gui.Application.instance.menubar is None:
            if isMacOS:
                app_menu = gui.Menu()
                app_menu.add_item("Quit", AppWindow.MENU_QUIT)
            file_menu = gui.Menu()
            file_menu.add_item("Open...", AppWindow.MENU_OPEN)
            if not isMacOS:
                file_menu.add_separator()
                file_menu.add_item("Quit", AppWindow.MENU_QUIT)
            settings_menu = gui.Menu()
            settings_menu.set_checked(AppWindow.MENU_SHOW_SETTINGS, True)


            menu = gui.Menu()
            if isMacOS:
                # macOS will name the first menu item for the running application
                # (in our case, probably "Python"), regardless of what we call
                # it. This is the application menu, and it is where the
                # About..., Preferences..., and Quit menu items typically go.
                menu.add_menu("Example", app_menu)
                menu.add_menu("File", file_menu)
                menu.add_menu("Settings", settings_menu)
                # Don't include help menu unless it has something more than
                # About...
            else:
                menu.add_menu("File", file_menu)
                menu.add_menu("Settings", settings_menu)
            gui.Application.instance.menubar = menu

        # The menubar is global, but we need to connect the menu items to the
        # window, so that the window can call the appropriate function when the
        # menu item is activated.
        w.set_on_menu_item_activated(AppWindow.MENU_OPEN, self._on_menu_open)
        w.set_on_menu_item_activated(AppWindow.MENU_QUIT, self._on_menu_quit)
        w.set_on_menu_item_activated(AppWindow.MENU_SHOW_SETTINGS,
                                     self._on_menu_toggle_settings_panel)
        # ----

        #Apply settings
        self._apply_settings()
def main():
    # We need to initialize the application, which finds the necessary shaders
    # for rendering and prepares the cross-platform window abstraction.
    gui.Application.instance.initialize()

    w = AppWindow(1024, 768)

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            w.load(path)
        else:
            w.window.show_message_box("Error",
                                      "Could not open file '" + path + "'")

    # Run the event loop. This will not return until the last window is closed.
    gui.Application.instance.run()


if __name__ == "__main__":
    main()