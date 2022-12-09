import sys
from os.path import join, isfile
from typing import Union, List
from random import sample

import numpy as np
import gmsh
import meshio
from sklearn.decomposition import PCA


class Mesh:
    
    def __init__(self, name: str, in_path: str, out_path: Union[None, str] = None, mesh_format: str = "inp") -> None:
        self.name = name
        self.in_path = in_path
        self.out_path = out_path if out_path is not None else in_path
        self.mesh_format = mesh_format
        self.mesh_name = f"{self.name}.{self.mesh_format}"
        
    def generate_mesh(
        self,
        min_size: int,
        max_size: int,
        geo_format: str = "step",
        visualize: bool = False,
    ) -> None:
        gmsh.initialize()

        gmsh.model.add(self.name)

        cad = f"{self.name}.{geo_format}"

        v = gmsh.model.occ.importShapes(join(self.in_path, cad))
        gmsh.model.occ.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMin", min_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", max_size)
        gmsh.model.mesh.generate(3)
        gmsh.write(join(self.out_path, self.mesh_name))

        if visualize:
            # Launch the GUI to see the results:
            if "-nopopup" not in sys.argv:
                gmsh.fltk.run()
            gmsh.finalize()


    def analyze_mesh(self) -> List[List[float]]:
        mesh_path = join(self.out_path, self.mesh_name)
        if not isfile(mesh_path):
            raise FileNotFoundError("Mesh file not found, check file format of run generate_mesh method first.")
        mesh = meshio.read(mesh_path)
        return mesh.points


class Meshes:
    def __init__(self, meshes: List[Mesh]) -> None:
        len_meshes = len(meshes)
        self.meshes_coordinates = [0]*len_meshes
        self.balanced_meshes_coordinates = [0]*len_meshes
        meshes_nnodes = [0]*len_meshes
        
        for c, mesh in enumerate(meshes):
            mesh_points = mesh.analyze_mesh()
            self.meshes_coordinates[c] = mesh_points
            meshes_nnodes[c] = len(mesh_points)
        
        max_nnodes = max(meshes_nnodes)
        missing_nodes = [max_nnodes - mesh_nnodes for mesh_nnodes in meshes_nnodes]
        
        j = 0
        for mesh_coordinates, missing_node in zip(self.meshes_coordinates, missing_nodes):
            if missing_node != 0:
                balanced_mesh_coordinates = np.append(mesh_coordinates, sample(list(mesh_coordinates), missing_node), axis=0) # to be replaced with oversampling, averaging nodes positions
            else:
                balanced_mesh_coordinates = mesh_coordinates
            self.balanced_meshes_coordinates[j] = balanced_mesh_coordinates
            j += 1
        
    def return_meshes_coordinates(self):
        return self.balanced_meshes_coordinates
        

if __name__ == "__main__":

    names = ["beam_40-20-15", "beam_50-10-10", "beam_50-20-10"]
    path = "tests\\utilties\\"
    min_size = 3
    max_size = 3
    visualize = True
    
    mesh_list = []
    
    for name in names:
        mesh = Mesh(name, in_path=path)
        mesh.generate_mesh(3, 3)
        mesh_list.append(mesh)
    
    meshes = Meshes(mesh_list)
    meshes_coordinates = meshes.return_meshes_coordinates() # needs reshaping --> is it possible in this context?
    new = np.reshape(meshes_coordinates, newshape=(3, 3*675))
    pca = PCA(n_components=2)
    pca.fit(new)

    print(pca.explained_variance_ratio_)
    print(pca.singular_values_)
    
    # for mesh_coordinates in meshes_coordinates:
    #     print(np.shape(mesh_coordinates))
