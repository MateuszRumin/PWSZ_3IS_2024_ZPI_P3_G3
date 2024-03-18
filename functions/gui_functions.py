from libraries import *

class GuiFunctions:

    def on_window_close(self):
        self.window.hide()
        return False
    def _set_mouse_mode_rotate(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_CAMERA)

    def _set_mouse_mode_fly(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.FLY)

    def _set_mouse_mode_sun(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_SUN)

    def _set_mouse_mode_ibl(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_IBL)

    def _set_mouse_mode_model(self):
        self._scene.set_view_controls(gui.SceneWidget.Controls.ROTATE_MODEL)

    def _on_set_set(self):
        if self.cloud is not None:
            transform_matrix = self._scene.scene.get_geometry_transform("__model__")
            transformed_point_cloud = self.cloud.transform(np.linalg.inv(transform_matrix))
            self.cloud = transformed_point_cloud
        if self.create_mesh is not None:
            transform_matrix = self._scene.scene.get_geometry_transform("__mesh__")
            transformed_mesh = self.create_mesh.transform(np.linalg.inv(transform_matrix))
            self.create_mesh = transformed_mesh

    def _on_bg_color(self, new_color):
        self.settings.bg_color = new_color
        self._apply_settings()

    def _on_show_axes(self, show):
        self.settings.show_axes = show
        self._apply_settings()

    def _on_enable_buttons(self):
        self.settings.enable_buttons = True
        self._apply_settings()

    def _on_enable_buttons_export(self):
        self.settings.enable_buttons_export = True
        self._apply_settings()

    def _on_sun_dir(self, sun_dir):
        self.settings.sun_dir = sun_dir
        self._profiles.selected_text = Settings.CUSTOM_PROFILE_NAME
        self._apply_settings()

    def _on_shader(self, name, index):
        self.settings.set_material(AppWindow.MATERIAL_SHADERS[index])
        self._apply_settings()

    def _on_material_prefab(self, name, index):
        self.settings.apply_material_prefab(name)
        self.settings.apply_material = True
        self._apply_settings()

    def _on_material_color(self, color):
        self.settings.material.base_color = [
            color.red, color.green, color.blue, color.alpha
        ]
        self.settings.apply_material = True
        self._apply_settings()

    def _on_point_size(self, size):
        self.settings.material.point_size = int(size)
        self.settings.apply_material = True
        self._apply_settings()

    def _on_menu_toggle_settings_panel(self):
        self._settings_panel.visible = not self._settings_panel.visible
        gui.Application.instance.menubar.set_checked(
            AppWindow.MENU_SHOW_SETTINGS, self._settings_panel.visible)

    def _on_points_checkbox(self, decision):
        self.settings.points_enabled = decision
        self._apply_settings()

    def _on_max_points_checkbox(self, decision):
        self.settings.max_points_enabled = decision
        self._apply_settings()

    def _on_normalize_points_checkbox(self, decision):
        self.settings.normalize_all_points = decision
        self._apply_settings()

    def _on_complement_slider_1_change(self, value):
        self.settings.complement_slider_1_value = int(value)

        if self.cloud is not None:
            self._scene.scene.remove_geometry("__model__")
            voxel_cloud = self.cloud.voxel_down_sample(voxel_size=(float(self.settings.complement_slider_1_value) / 10000))
            self.cloud = voxel_cloud
            self._scene.scene.add_geometry("__model__", self.cloud, self.settings.material)

        self._apply_settings()

    def _reset_object(self):
        self._scene.scene.remove_geometry("__model__")
        self.cloud = self.cloud_backup
        self._scene.scene.add_geometry("__model__", self.cloud, self.settings.material)


    def _on_complement_slider_2_change(self, value):
        self.settings.complement_slider_2_value = int(value)

        if self.cloud is not None:
            self._scene.scene.remove_geometry("__model__")
            scale_factor = (float(self.settings.complement_slider_2_value) - 1) / 99 * -0.9999 + 1
            center = self.cloud.get_center()
            scale_cloud = self.cloud.scale(scale_factor, center=center)
            self.cloud = scale_cloud
            self._scene.scene.add_geometry("__model__", self.cloud, self.settings.material)

        self._apply_settings()

    def _on_complement_slider_3_change(self, value):
        self.settings.complement_slider_3_value = int(value)

        if self.cloud is not None:
            self._scene.scene.remove_geometry("__model__")
            scale_factor = (float(self.settings.complement_slider_3_value) - 1) / 99 * 9 + 1
            center = self.cloud.get_center()
            scale_cloud = self.cloud.scale(scale_factor, center=center)
            self.cloud = scale_cloud
            self._scene.scene.add_geometry("__model__", self.cloud, self.settings.material)

        self._apply_settings()

    def _add_geometry_name(self, name):
        geometry_names = [geom[0] for geom in self.settings.geometry_visibility]

        if name not in geometry_names:
            self.settings.add_geometry_name_to_table(name)
            self._add_element_to_tree(name)



    def _add_element_to_tree(self, name, visibility=True):
        self.geometry_models_tree.add_item(self.root, gui.CheckableTextTreeCell(
            name, visibility, lambda value, name=name: self.geometry_models_tree_check(name, value)
        ))

    def geometry_models_tree_check(self, name, value):
        for geom, visibility in self.settings.geometry_visibility:
            if geom == name:
                if visibility:
                    self.settings.toggle_visibility_true_to_false(geom)
                    self._scene.scene.show_geometry(geom, False)
                else:
                    self.settings.toggle_visibility_false_to_true(geom)
                    self._scene.scene.show_geometry(geom, True)
                break
