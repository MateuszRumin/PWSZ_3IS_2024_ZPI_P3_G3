import math
import copy

import numpy as np

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
        self._apply_settings()
        self._transform_object()

    def _change_scale(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.scale_value = round((self.settings.scale_value + 0.1), 1)
            elif key == "-":
                if self.settings.scale_value > 0.1:
                    self.settings.scale_value = round((self.settings.scale_value - 0.1), 1)
        self._apply_settings()
        self._transform_object()


    def _on_complement_slider_3_change(self, value):
        self.settings.complement_slider_3_value = int(value)
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

    def move_in_x_axis(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.object_move_in_x_direction += 0.005
            elif key == "-":
                self.settings.object_move_in_x_direction -= 0.005
            self._transform_object()


    def move_in_y_axis(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.object_move_in_y_direction += 0.005
            elif key == "-":
                self.settings.object_move_in_y_direction -= 0.005
            self._transform_object()


    def move_in_z_axis(self, key):
        if self.cloud is not None:
            if key == "+":
                self.settings.object_move_in_z_direction += 0.005
            elif key == "-":
                self.settings.object_move_in_z_direction -= 0.005
            self._transform_object()


    def _rotation_slider_x_change(self, value):
        if self.cloud is not None:
            self.settings.rotate_slider_x_value = int(value)
            self._apply_settings()
            self._transform_object()

    def _rotation_slider_y_change(self, value):
        if self.cloud is not None:
            self.settings.rotate_slider_y_value = int(value)
            self._apply_settings()
            self._transform_object()

    def _rotation_slider_z_change(self, value):
        if self.cloud is not None:
            self.settings.rotate_slider_z_value = int(value)
            self._apply_settings()
            self._transform_object()


    def _transform_object(self):
        self.cloud = copy.deepcopy(self.cloud_backup)
        self._scene.scene.remove_geometry("__model__")

        theta_x = math.radians(int(self.settings.rotate_slider_x_value))
        theta_y = math.radians(int(self.settings.rotate_slider_y_value))
        theta_z = math.radians(int(self.settings.rotate_slider_z_value))

        R_x = np.array([
            [1, 0, 0],
            [0, np.cos(theta_x), -np.sin(theta_x)],
            [0, np.sin(theta_x), np.cos(theta_x)]
        ])

        R_y = np.array([
            [np.cos(theta_y), 0, np.sin(theta_y)],
            [0, 1, 0],
            [-np.sin(theta_y), 0, np.cos(theta_y)]
        ])

        R_z = np.array([
            [np.cos(theta_z), -np.sin(theta_z), 0],
            [np.sin(theta_z), np.cos(theta_z), 0],
            [0, 0, 1]
        ])

        R = np.dot(R_z, np.dot(R_y, R_x))

        transform = np.eye(4)
        transform[0, 3] = self.settings.object_move_in_x_direction
        transform[1, 3] = self.settings.object_move_in_y_direction
        transform[2, 3] = self.settings.object_move_in_z_direction

        transform_cloud = self.cloud.transform(transform)
        self.cloud = transform_cloud

        voxel_cloud = self.cloud.voxel_down_sample(voxel_size=(float(self.settings.complement_slider_1_value) / 10000))
        self.cloud = voxel_cloud

        self.cloud.rotate(R, center=self.cloud.get_center())

        self.cloud.scale(self.settings.scale_value, center=self.cloud.get_center())

        self._scene.scene.add_geometry("__model__", self.cloud, self.settings.material)

        if self.create_mesh is not None:
            self._scene.scene.remove_geometry("__mesh__")
            self.create_mesh = copy.deepcopy(self.create_mesh_backup)
            transform_mesh = self.create_mesh.transform(transform)
            self.create_mesh = transform_mesh
            self.create_mesh.rotate(R, center=self.create_mesh.get_center())
            self.create_mesh.scale(self.settings.scale_value, center=self.cloud.get_center())
            self._scene.scene.add_geometry("__mesh__", self.create_mesh, self.settings.material)

        self._apply_settings()

    def on_point_selection(self, event):
        if event.type == gui.MouseEvent.Type.BUTTON_DOWN and event.is_button_down(gui.MouseButton.LEFT) and event.is_modifier_down(gui.KeyModifier.CTRL):
            def depth_callback(depth_image):
                x = event.x - self._scene.frame.x
                y = event.y - self._scene.frame.y

                depth = np.asarray(depth_image)[x, y]

                # Adjust the depth value check or interpretation as needed
                if depth == 1.0:
                    text = ""
                else:
                    world = self._scene.scene.camera.unproject(x, y, depth, self._scene.frame.width, self._scene.frame.height)

                    text = "({:.3f}, {:.3f}, {:.3f})".format(world[0],world[1],world[2])

                    idx = self._calc_prefer_indicate(world)
                    true_point = np.asarray(self.cloud.points)[idx]

                    self._pick_num += 1
                    self._picked_indicates.append(idx)
                    self._picked_points.append(true_point)


                    print(f"Pick point #{idx} at ({true_point[0]}, {true_point[1]}, {true_point[2]})")

                def draw_point():
                    self._info.text = text
                    self._info.visible = (text != "")
                    self.window.set_needs_layout()

                    if depth != 1.0:
                        label3d = self._scene.add_3d_label(true_point, "#"+str(self._pick_num))
                        self._label3d_list.append(label3d)

                        sphere = o3d.geometry.TriangleMesh.create_sphere(0.0025)
                        sphere.paint_uniform_color([1,0,0])
                        sphere.translate(true_point)
                        material = rendering.MaterialRecord()
                        material.shader = 'defaultUnlit'
                        self._scene.scene.add_geometry("sphere"+str(self._pick_num),sphere,material)
                        self._scene.force_redraw()

                gui.Application.instance.post_to_main_thread(self.window, draw_point)

            self._scene.scene.scene.render_to_depth_image(depth_callback)
            return gui.Widget.EventCallbackResult.HANDLED
        elif event.type == gui.MouseEvent.Type.BUTTON_DOWN and event.is_button_down(gui.MouseButton.RIGHT) and event.is_modifier_down(gui.KeyModifier.CTRL):
            if self._pick_num > 0:
                idx = self._picked_indicates.pop()
                point = self._picked_points.pop()

                print(f"Undo pick: #{idx} at ({point[0]}, {point[1]}, {point[2]})")

                self._scene.scene.remove_geometry('sphere'+str(self._pick_num))
                self._pick_num -= 1
                self._scene.remove_3d_label(self._label3d_list.pop())
                self._scene.force_redraw()
            else:
                print("Undo no point!")
            return gui.Widget.EventCallbackResult.HANDLED
        else:
            return gui.Widget.EventCallbackResult.IGNORED


    def _calc_prefer_indicate(self, point):
        cloud = copy.deepcopy(self.cloud)
        cloud.points.append(np.asarray(point))

        cloud_tree = o3d.geometry.KDTreeFlann(cloud)
        [k, idx, _] = cloud_tree.search_knn_vector_3d(cloud.points[-1], 2)
        return idx[-1]

