"""
################################################################################################
||                                                                                            ||
||                                        Mesh Creator                                        ||
||                                                                                            ||
||             This file contains functions for generating and repairing the mesh             ||
||                                                                                            ||
################################################################################################
"""
import os
import copy
import time
import numpy as np
import pymeshfix
import open3d as o3d
import pyvista as pv
import tempfile
import threading
import torch
from tkinter import messagebox
from argparse import Namespace
from functions import time_factory
from triangulate.point_tri_net import PointTriNet_Mesher
from triangulate.mesh_utils import fill_holes_greedy
from triangulate.utils import set_args_defaults
import traceback


def convert_to_tensor(cloud,device,dtype):

    samples = torch.tensor(np.asarray(cloud.points), dtype=dtype, device=device)
    return samples


def calculate_radii(point_cloud, num_neighbors=2):
    distances = np.array(point_cloud.compute_nearest_neighbor_distance())
    avg_d = np.mean(distances)
    par = 1* avg_d

    radii = [par,1.1*par,1.2*par,1.3*par,1.4*par, 1.5*par,1.6*par,1.7*par,1.8*par,1.9*par,2*par,
             1.9*par, 1.8*par, 1.7*par, 1.6*par, 1.5*par, 1.4*par, 1.3*par, 1.2*par, 1.1*par, par,
             0.9*par,0.8*par,0.7*par,
             2.1*par,2.2*par,2.3*par,2.4*par, 2.5*par,2.6*par,2.7*par,2.8*par,2.9*par, 3*par]
    # radii = [par,2*par]
    return radii


def triangulate_bpa(cloud,radii):

    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud,o3d.utility.DoubleVector(radii))
    # mesh = mesh.simplify_quadric_decimation(100000)
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    mesh.compute_vertex_normals()

    return mesh


def triangulate_poisson(cloud):


    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud, depth=8, width=0, scale=1, linear_fit=True)
    poisson_mesh = mesh[0]
    bbox = cloud.get_axis_aligned_bounding_box()
    p_mesh_crop = poisson_mesh.crop(bbox)
    p_mesh_crop.compute_vertex_normals()
    p_mesh_crop.paint_uniform_color([0.5, 0.5, 0.5])


    return p_mesh_crop


class MeshCreator():

    def _make_mesh(self):
        if self.cloud is not None:
            self.show_loading_window()
            thread = threading.Thread(target=self._make_mesh_thread)
            thread.start()

    def _make_mesh_thread(self):
        if self.normalize_checkbox.isChecked() and self.cloud is not None:
            try:
                MyTimer = time_factory.timer_factory()
                with MyTimer('Mesh Creation after normalization'):
                    self.removeActorSignal.emit("mesh")
                    self.normalizeCloud()

                    cloud = self.open3d_normalized_cloud




                    # Creating open3d mesh
                    # radii = calculate_radii(cloud)
                    # rec_mesh = triangulate_bpa(cloud,radii)
                    rec_mesh = triangulate_poisson(cloud)
                    # print("jestem")
                    # par = np.mean(cloud.compute_nearest_neighbor_distance())

                    # Creating open3d mesh
                    # radii = [0.005, 0.01, 0.015, 0.02, 0.025]
                    # # radii = [0.9 * par, 0.91 * par, 0.92 * par, 0.93 * par, 0.94 * par, 0.95 * par, 0.96 * par, 0.97 * par,
                    # #          0.98 * par, 0.99 * par,
                    # #          1 * par, 1.01 * par, 1.02 * par, 1.03 * par, 1.04 * par, 1.05 * par, 1.06 * par, 1.07 * par,
                    # #          1.08 * par, 1.09 * par,
                    # #          1.1 * par, 1.11 * par, 1.12 * par, 1.13 * par, 1.14 * par, 1.15 * par, 1.16 * par, 1.17 * par,
                    # #          1.18 * par, 1.19 * par,
                    # #          1.2 * par, 1.21 * par, 1.22 * par, 1.23 * par, 1.24 * par, 1.25 * par, 1.26 * par, 1.27 * par,
                    # #          1.28 * par, 1.29 * par,
                    # #          1.3 * par, 1.4 * par, 1.5 * par, 1.6 * par, 1.75 * par, 0.01, 0.02, 0.04]
                    # rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(cloud,
                    #                                                                            o3d.utility.DoubleVector(radii))

                    # a = o3d.utility.Vector3dVector(rec_mesh.triangles)

                    # print(f"a", len(np.asarray(a)))

                     # rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(cloud, depth=6, linear_fit=False, n_threads=4 )
                    #
                    # rec_mesh = o3d.geometry.TriangleMesh(rec_mesh[0])

                    if self.settings.enable_triangles_amount_input_field:
                        triangles_amount = len(rec_mesh.triangles)
                        triangles_amount_calculated = (triangles_amount * (self.settings.triangles_amount / 100))
                        simplified_mesh = rec_mesh.simplify_quadric_decimation(
                            target_number_of_triangles=int(triangles_amount_calculated))  # Changing triangles amount
                        rec_mesh = simplified_mesh

                    # if self.origin_vectors_normalized is None:
                    #     pcd = rec_mesh.sample_points_poisson_disk(5000)
                    #
                    #     pcd.normals = o3d.utility.Vector3dVector(np.zeros(
                    #         (1, 3)))  # invalidate existing normals
                    # ----------------------

                    #Transform mesh from open3d to pyvsita
                    v = np.asarray(rec_mesh.vertices)
                    f = np.array(rec_mesh.triangles)
                    f = np.c_[np.full(len(f), 3), f]
                    mesh = pv.PolyData(v, f)
                    #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                    # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                    #     self.create_mesh.save(self.create_mesh_backup.name)

                    self.assignMeshSignal.emit(mesh)
                    self.overwriteBackupMeshSignal.emit(mesh)

                    #Add to plotter
                    #self.remove_mesh()
                    self.addMeshSignal.emit(mesh)
                    #self.add_mesh_to_plotter(self.create_mesh)
                    #time.sleep(1)   #Fix for window freeze xd
                    #self.close_loading_window()
                        # ------------------------------
            except Exception as e:
                print("[WARNING] Failed to create mesh with normals", e)
                messagebox.showerror('Python Error', e)
                self.resetPlotterSignal.emit()
            finally:
                del self.open3d_normalized_cloud
        else:
            try:
                MyTimer = time_factory.timer_factory()
                with MyTimer('Mesh Creation without normalization'):
                    self.removeActorSignal.emit("mesh")

                    # Converting pyvista cloud to open3d cloud
                    args = Namespace(
                        model_weights_path='./triangulate/model/model_state_dict.pth',
                        disable_cuda=False if torch.cuda.is_available() else True,
                        n_rounds=5,
                        prob_thresh=0.9,
                    )

                    set_args_defaults(args)

                    MyTimer = time_factory.timer_factory()
                    with MyTimer('Mesh Creation after normalization'):
                        model = PointTriNet_Mesher()

                        model.load_state_dict(torch.load(args.model_weights_path, map_location=args.device))

                        model.eval()
                        # self.normalizeCloud()
                        # cloud = self.open3d_normalized_cloud

                        with torch.no_grad():
                            candidate_triangles, candidate_probs = model.predict_mesh(
                                convert_to_tensor(self.cloud, args.device, args.dtype).unsqueeze(0),
                                n_rounds=args.n_rounds)
                            candidate_triangles = candidate_triangles.squeeze(0)
                            candidate_probs = candidate_probs.squeeze(0)

                            high_prob = candidate_triangles[candidate_probs > args.prob_thresh]
                            # high_prob_faces = fill_holes_greedy(high_prob)

                        rec_mesh = o3d.geometry.TriangleMesh()

                        rec_mesh.vertices = o3d.utility.Vector3dVector(self.cloud.points)
                        triangles = high_prob.cpu().numpy()
                        rec_mesh.triangles = o3d.utility.Vector3iVector(triangles)

                    if self.settings.enable_triangles_amount_input_field:
                        triangles_amount = len(rec_mesh.triangles)
                        triangles_amount_calculated = (triangles_amount * (self.settings.triangles_amount / 100))
                        simplified_mesh = rec_mesh.simplify_quadric_decimation(
                            target_number_of_triangles=int(triangles_amount_calculated))  # Changing triangles amount
                        rec_mesh = simplified_mesh


                    pcd = rec_mesh.sample_points_poisson_disk(5000)

                    pcd.normals = o3d.utility.Vector3dVector(np.zeros(
                        (1, 3)))  # invalidate existing normals
                    # ----------------------

                    # Transform mesh from open3d to pyvsita
                    v = np.asarray(rec_mesh.vertices)
                    f = np.array(rec_mesh.triangles)
                    f = np.c_[np.full(len(f), 3), f]
                    mesh = pv.PolyData(v, f)
                    #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                    # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                    #     self.create_mesh.save(self.create_mesh_backup.name)

                    self.assignMeshSignal.emit(mesh)
                    self.overwriteBackupMeshSignal.emit(mesh)

                    # Reloading mesh
                    self.addMeshSignal.emit(mesh)
                    #self.remove_mesh()
                    #self.add_mesh_to_plotter(self.create_mesh)
                    # ------------------------------
            except Exception as e:
                print("[WARNING] Failed to create mesh without normalization", e)
                messagebox.showerror('Python Error', e)
                self.resetPlotterSignal.emit()

    def repair_mesh(self):
        if self.create_mesh is not None:
            self.show_loading_window()
            thread = threading.Thread(target=self.repair_mesh_thread)
            thread.start()

    def repair_mesh_thread(self):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Mesh Fix'):
            if self.create_mesh is not None:
                try:
                    self.removeActorSignal.emit("mesh")

                    # Generate a meshfix mesh ready for fixing and extract the holes
                    meshfix = pymeshfix.MeshFix(self.create_mesh)
                    holes = meshfix.extract_holes()

                    # Repair the mesh
                    meshfix.repair(verbose=True, joincomp=True, remove_smallest_components=True)
                    mesh = meshfix.mesh

                    # Split mesh by components


                    self.overwriteBackupMeshSignal.emit(mesh)
                    self.assignMeshSignal.emit(mesh)

                    # Reloading mesh
                    self.addMeshSignal.emit(mesh)

                except Exception as e:
                    print("[WARNING] Failed to fix mesh", e)
                    messagebox.showerror('Python Error', e)
                    self.resetPlotterSignal.emit()

    def transform_existing_mesh(self):
        if self.create_mesh is not None and self.settings.enable_triangles_amount_input_field:
            self.show_loading_window()
            thread = threading.Thread(target=self.transform_existing_mesh_thread)
            thread.start()

    def transform_existing_mesh_thread(self):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Triangles reduction'):
            if self.create_mesh is not None:
                self.removeActorSignal.emit("mesh")
                if self.settings.transformation_logic_equalizer != [0, 0, 0, 0]:
                    if self.settings.transformation_logic_equalizer != [0, 1, 0, 0]:
                        #Overwrite backup and save changes in equalizer
                        #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                        # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                        #     self.create_mesh.save(self.create_mesh_backup.name)
                        self.overwriteBackupMeshSignal.emit(self.create_mesh)

                        self.settings.transformation_logic_equalizer = [0, 1, 0, 0]
                        self.settings.reset_transformation_values()
                        self.settings.reset_smooth_values()
                        self.settings.reset_subdivide_values()
                        self._apply_settings()
                        #----------------------------------------------

                if self.settings.transformation_logic_equalizer == [0, 0, 0, 0] or self.settings.transformation_logic_equalizer == [0, 1, 0, 0]:
                    try:
                        #Triangles reduction
                        print(f"Number of triangles in mesh: {self.create_mesh.n_points}")
                        if self.settings.enable_triangles_amount_input_field:
                            #self.create_mesh = copy.deepcopy(self.create_mesh_backup)

                            self.create_mesh = pv.read(self.create_mesh_backup.name)

                            reduction_value = ((float(self.settings.triangles_amount) - 100) * (-1)) / 100
                            if reduction_value < 1:
                                self.create_mesh = self.create_mesh.decimate(reduction_value)
                        print(f"Number of triangles in mesh after reduction: {self.create_mesh.n_points}")

                        # Reloading mesh
                        self.addMeshSignal.emit(self.create_mesh)

                        #self.remove_mesh()
                        #self.add_mesh_to_plotter(self.create_mesh)
                        self.settings.transformation_logic_equalizer = [0, 1, 0, 0]
                        # ------------------------------
                    except Exception as e:
                        print("[WARNING] Failed to change number of triangles", e)
                        messagebox.showerror('Python Error', e)
                        self.resetPlotterSignal.emit()

    def _smooth_mesh(self):
        if self.create_mesh is not None:
            self.show_loading_window()
            thread = threading.Thread(target=self._smooth_mesh_thread)
            thread.start()

    def _smooth_mesh_thread(self):
        MyTimer = time_factory.timer_factory()
        with MyTimer('Mesh Smooth'):
            if self.create_mesh is not None:
                if self.settings.transformation_logic_equalizer != [0, 0, 0, 0]:
                    if self.settings.transformation_logic_equalizer != [0, 0, 1, 0]:
                        #Overwrite backup and save changes in equalizer
                        #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                        # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                        #     self.create_mesh.save(self.create_mesh_backup.name)
                        self.overwriteBackupMeshSignal.emit(self.create_mesh)

                        self.settings.transformation_logic_equalizer = [0, 0, 1, 0]
                        self.settings.reset_transformation_values()
                        self.settings.reset_triangles_values()
                        self.settings.reset_subdivide_values()
                        self._apply_settings()
                        #----------------------------------------------

                if self.settings.transformation_logic_equalizer == [0, 0, 0, 0] or self.settings.transformation_logic_equalizer == [0, 0, 1, 0]:
                    if int(self.settings.number_of_smooth_iterations) > 0:
                        try:
                            self.removeActorSignal.emit("mesh")
                            #self.create_mesh = copy.deepcopy(self.create_mesh_backup)

                            self.create_mesh = pv.read(self.create_mesh_backup.name)


                            vertices = self.create_mesh.points
                            faces = self.create_mesh.faces.reshape(-1, 4)[:, 1:]

                            o3d_vertices = o3d.utility.Vector3dVector(vertices)
                            o3d_faces = o3d.utility.Vector3iVector(faces)

                            o3d_mesh = o3d.geometry.TriangleMesh()
                            o3d_mesh.vertices = o3d_vertices
                            o3d_mesh.triangles = o3d_faces

                            mesh_in = o3d_mesh
                            vertices = np.asarray(mesh_in.vertices)

                            #print('filter with average with n iteration')
                            n = int(self.settings.number_of_smooth_iterations)
                            mesh_out = mesh_in.filter_smooth_simple(number_of_iterations=n)
                            mesh_out.compute_vertex_normals()

                            v = np.asarray(mesh_out.vertices)
                            f = np.array(mesh_out.triangles)
                            f = np.c_[np.full(len(f), 3), f]
                            mesh = pv.PolyData(v, f)

                            self.create_mesh = mesh

                            #self.remove_mesh()
                            self.addMeshSignal.emit(self.create_mesh)
                            #self.add_mesh_to_plotter(self.create_mesh)
                            self.settings.transformation_logic_equalizer = [0, 0, 1, 0]
                        except Exception as e:
                            print("[WARNING] Failed to smooth mesh", e)
                            messagebox.showerror('Python Error', e)
                            self.resetPlotterSignal.emit()
                    else:
                        self.removeActorSignal.emit("mesh")
                        #self.create_mesh = self.create_mesh_backup

                        self.create_mesh = pv.read(self.create_mesh_backup.name)
                        self.addMeshSignal.emit(self.create_mesh)

                        #self.remove_mesh()
                        #self.add_mesh_to_plotter(self.create_mesh)

    def _subdevide_triangles(self):
        if self.create_mesh is not None:
            self.show_loading_window()
            thread = threading.Thread(target=self._subdevide_triangles_thread)
            thread.start()

    def _subdevide_triangles_thread(self):
        if self.create_mesh is not None:
            MyTimer = time_factory.timer_factory()
            with MyTimer('Subdivide triangles'):
                #Logic equalizer
                if self.settings.transformation_logic_equalizer != [0, 0, 0, 0]:
                    if self.settings.transformation_logic_equalizer != [0, 0, 0, 1]:
                        #Overwrite backup and save changes in equalizer
                        #self.create_mesh_backup = copy.deepcopy(self.create_mesh)

                        # with tempfile.NamedTemporaryFile(suffix='.vtk', delete=False) as self.create_mesh_backup:
                        #     self.create_mesh.save(self.create_mesh_backup.name)
                        self.overwriteBackupMeshSignal.emit(self.create_mesh)

                        self.settings.transformation_logic_equalizer = [0, 0, 0, 1]
                        self.settings.reset_transformation_values()
                        self.settings.reset_triangles_values()
                        self.settings.reset_smooth_values()
                        self._apply_settings()
                        #----------------------------------------------

                if self.settings.transformation_logic_equalizer == [0, 0, 0, 0] or self.settings.transformation_logic_equalizer == [0, 0, 0, 1]:
                    if self.subdivideselect.currentText() == 'None':
                        self.resetPlotterSignal.emit()
                        pass

                    #Linear subdivide
                    elif self.subdivideselect.currentText() == 'Subdivide - Linear':
                        try:
                            #self.create_mesh = self.create_mesh_backup.subdivide(int(self.settings.number_of_subdevide_iteration), 'linear')
                            self.create_mesh = pv.read(self.create_mesh_backup.name)
                            self.create_mesh = self.create_mesh.subdivide(int(self.settings.number_of_subdevide_iteration), 'linear')
                            #self._reset_plotter()
                            self.resetPlotterSignal.emit()
                            # self.create_mesh_backup = copy.deepcopy(self.create_mesh)
                        except Exception as e:
                            print("[WARNING] Failed to subdivide mesh", e)
                            messagebox.showerror('Python Error', e)
                            self.resetPlotterSignal.emit()

                    #Buteterfly subdivide
                    elif self.subdivideselect.currentText() == 'Subdivide - butterfly':
                        try:
                            #self.create_mesh = self.create_mesh_backup.subdivide(int(self.settings.number_of_subdevide_iteration), 'butterfly')
                            self.create_mesh = pv.read(self.create_mesh_backup.name)
                            self.create_mesh = self.create_mesh.subdivide(int(self.settings.number_of_subdevide_iteration), 'butterfly')
                            #self._reset_plotter()
                            self.resetPlotterSignal.emit()
                        except Exception as e:
                            print("[WARNING] Failed to subdivide mesh", e)
                            messagebox.showerror('Python Error', e)
                            self.resetPlotterSignal.emit()

                    #Loop subdivide
                    elif self.subdivideselect.currentText() == 'Subdivide - Loop':
                        try:
                            #self.create_mesh = self.create_mesh_backup.subdivide(int(self.settings.number_of_subdevide_iteration), 'loop')
                            self.create_mesh = pv.read(self.create_mesh_backup.name)
                            self.create_mesh = self.create_mesh.subdivide(int(self.settings.number_of_subdevide_iteration), 'loop')
                            #self._reset_plotter()
                            self.resetPlotterSignal.emit()
                        except Exception as e:
                            print("[WARNING] Failed to subdivide mesh", e)
                            messagebox.showerror('Python Error', e)
                            self.resetPlotterSignal.emit()

                    # Midpoint subdivide in open3d
                    elif self.subdivideselect.currentText() == 'Midpoint Open3D':
                        try:
                            #Convert pyvista mesh to open3d mesh
                            #self.create_mesh = copy.deepcopy(self.create_mesh_backup)
                            self.create_mesh = pv.read(self.create_mesh_backup.name)
                            vertices = self.create_mesh.points
                            faces = self.create_mesh.faces.reshape(-1, 4)[:, 1:]

                            o3d_vertices = o3d.utility.Vector3dVector(vertices)
                            o3d_faces = o3d.utility.Vector3iVector(faces)

                            o3d_mesh = o3d.geometry.TriangleMesh()
                            o3d_mesh.vertices = o3d_vertices
                            o3d_mesh.triangles = o3d_faces
                            #-----------------------------------

                            #Subdivide operation
                            mesh_in = o3d_mesh
                            vertices = np.asarray(mesh_in.vertices)

                            n = int(self.settings.number_of_subdevide_iteration)
                            mesh_out = mesh_in.subdivide_midpoint(number_of_iterations=n)

                            mesh_out.compute_vertex_normals()
                            #-------------------

                            #Convert open3d mesh to pyvista
                            v = np.asarray(mesh_out.vertices)
                            f = np.array(mesh_out.triangles)
                            f = np.c_[np.full(len(f), 3), f]
                            mesh = pv.PolyData(v, f)
                            self.create_mesh = mesh
                            #self._reset_plotter()
                            self.resetPlotterSignal.emit()
                            #------------------------------
                        except Exception as e:
                            print("[WARNING] Failed to subdivide mesh", e)
                            messagebox.showerror('Python Error', e)
                            self.resetPlotterSignal.emit()

                    #Loop subdivide in open3d
                    elif self.subdivideselect.currentText() == 'Loop Open3D':
                        try:
                            #Convert pyvista mesh to open3d mesh
                            #self.create_mesh = copy.deepcopy(self.create_mesh_backup)
                            self.create_mesh = pv.read(self.create_mesh_backup.name)
                            vertices = self.create_mesh.points
                            faces = self.create_mesh.faces.reshape(-1, 4)[:, 1:]

                            o3d_vertices = o3d.utility.Vector3dVector(vertices)
                            o3d_faces = o3d.utility.Vector3iVector(faces)

                            o3d_mesh = o3d.geometry.TriangleMesh()
                            o3d_mesh.vertices = o3d_vertices
                            o3d_mesh.triangles = o3d_faces
                            #-----------------------------------

                            #Subdivide operation
                            mesh_in = o3d_mesh
                            vertices = np.asarray(mesh_in.vertices)

                            n = int(self.settings.number_of_subdevide_iteration)
                            mesh_out = mesh_in.subdivide_loop(number_of_iterations=n)

                            mesh_out.compute_vertex_normals()
                            #-------------------

                            #Convert open3d mesh to pyvista
                            v = np.asarray(mesh_out.vertices)
                            f = np.array(mesh_out.triangles)
                            f = np.c_[np.full(len(f), 3), f]
                            mesh = pv.PolyData(v, f)
                            self.create_mesh = mesh
                            #self._reset_plotter()
                            self.resetPlotterSignal.emit()
                            #------------------------------
                        except Exception as e:
                            print("[WARNING] Failed to subdivide mesh", e)
                            messagebox.showerror('Python Error', e)
                            self.resetPlotterSignal.emit()