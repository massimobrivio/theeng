import sys
from os.path import join, isfile
from typing import Union, List
from random import sample

import numpy as np
import gmsh
import meshio
from sklearn.decomposition import PCA


class Geometry:
    
    def __init__(self, name: str, in_path: str, out_path: Union[None, str] = None, geo_format: str = "stl") -> None:
        self.name = name
        self.in_path = in_path
        self.out_path = out_path if out_path is not None else in_path
        self.geo_name = f"{self.name}.{geo_format}"
        
    def analyze_geometry(self) -> List[List[float]]:
        geometry_path = join(self.out_path, self.geo_name)
        if not isfile(geometry_path):
            raise FileNotFoundError("Geometry file not found, check file format.")
        geometry = meshio.read(geometry_path)
        return geometry.points
    
    def generate_mesh(
        self,
        min_size: int,
        max_size: int,
        mesh_format: str = "inp",
        visualize: bool = False,
    ) -> None:
        gmsh.initialize()

        gmsh.model.add(self.name)

        mesh_name = f"{self.name}.{mesh_format}"

        v = gmsh.model.occ.importShapes(join(self.in_path, self.geo_name))
        gmsh.model.occ.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMin", min_size)
        gmsh.option.setNumber("Mesh.MeshSizeMax", max_size)
        gmsh.model.mesh.generate(3)
        gmsh.write(join(self.out_path, mesh_name))

        if visualize:
            # Launch the GUI to see the results:
            if "-nopopup" not in sys.argv:
                gmsh.fltk.run()
            gmsh.finalize()


class Geometries:
    def __init__(self, geometries: List[Geometry]) -> None:
        len_geometries = len(geometries)
        self.geo_coordinates = [0]*len_geometries
        self.balanced_geos_coordinates = [0]*len_geometries
        geo_npoints = [0]*len_geometries
        
        for c, geometry in enumerate(geometries):
            geometry_points = geometry.analyze_geometry()
            self.geo_coordinates[c] = geometry_points
            geo_npoints[c] = len(geometry_points)
        
        max_npoints = max(geo_npoints)
        missing_points = [max_npoints - geo_npoint for geo_npoint in geo_npoints]
        
        j = 0
        for geo_coordinate, missing_point in zip(self.geo_coordinates, missing_points):
            if missing_point != 0:
                balanced_geo_coordinates = np.append(geo_coordinate, [geo_coordinate[-1] for _ in range(missing_point)], axis=0)  # sample(list(geo_coordinate), missing_point), axis=0) # to be replaced with oversampling, averaging nodes positions
            else:
                balanced_geo_coordinates = geo_coordinate
            self.balanced_geos_coordinates[j] = balanced_geo_coordinates
            j += 1
        
    def return_geo_coordinates(self):
        return self.balanced_geos_coordinates
        

if __name__ == "__main__":

    names = ["beam_10-10-10", "beam_20-15-10", "beam_50-10-20", "beam_50-10-20_ciao"]
    path = "tests\\utilties\\"
    min_size = 3
    max_size = 3
    visualize = True
    
    geometry_list = []
    
    for name in names:
        geometry = Geometry(name, in_path=path)
        geometry_list.append(geometry)
    
    geometryes = Geometries(geometry_list)
    geometries_coordinates = geometryes.return_geo_coordinates() 
    print(geometries_coordinates)
    new = np.reshape(geometries_coordinates, newshape=(3, len(geometries_coordinates)*len(geometries_coordinates[0])))
    pca = PCA(n_components=2)
    pca.fit(new)

    print(pca.explained_variance_ratio_)
    print(pca.singular_values_)
    
    # https://pymesh.readthedocs.io/en/latest/api_misc.html#mesh-to-graph contains methods to remesh, remove vertices and converting mesh to graph
    # to work with point clouds this could be a library: http://www.open3d.org/docs/0.9.0/python_api/open3d.geometry.PointCloud.html