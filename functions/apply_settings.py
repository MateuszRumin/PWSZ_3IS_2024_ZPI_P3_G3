from libraries import *

class ApplySettings:
    DEFAULT_IBL = "default"

    MATERIAL_NAMES = ["Lit", "Unlit", "Normals", "Depth"]
    MATERIAL_SHADERS = [
        Settings.LIT, Settings.UNLIT, Settings.NORMALS, Settings.DEPTH
    ]

    def _apply_settings(self):
        bg_color = [
            self.settings.bg_color.red, self.settings.bg_color.green,
            self.settings.bg_color.blue, self.settings.bg_color.alpha
        ]
        self._scene.scene.set_background(bg_color)
        self._scene.scene.show_axes(self.settings.show_axes)

        self._bg_color.color_value = self.settings.bg_color
        self._show_axes.checked = self.settings.show_axes
        self.make_mesh_button.enabled = self.settings.enable_buttons
        self.edit_points_button.enabled = self.settings.enable_buttons
        self.export_to_obj_button.enabled = self.settings.enable_buttons_export
        self.export_to_stl_button.enabled = self.settings.enable_buttons_export
        self._points_number.enabled = self.settings.points_enabled
        self._max_points_numer.enabled = self.settings.max_points_enabled
        self._normalize_points_checkbox.checked = self.settings.normalize_all_points

        self._complement_slider_1.double_value = self.settings.complement_slider_1_value
        self._complement_slider_2.double_value = self.settings.complement_slider_2_value
        self._complement_slider_3.double_value = self.settings.complement_slider_3_value


        if self.settings.apply_material:
            self._scene.scene.update_material(self.settings.material)
            self.settings.apply_material = False

        self._material_prefab.enabled = (
                self.settings.material.shader == Settings.LIT)
        c = gui.Color(self.settings.material.base_color[0],
                      self.settings.material.base_color[1],
                      self.settings.material.base_color[2],
                      self.settings.material.base_color[3])
        self._material_color.color_value = c
        self._point_size.double_value = self.settings.material.point_size


