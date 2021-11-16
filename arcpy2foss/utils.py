from typing import Any

import pyproj
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform


def reproject(from_crs: Any, to_crs: Any, geom: BaseGeometry) -> BaseGeometry:
    """Reproject shapely geometry from a source to target coordinate reference
    system

    Parameters
    ----------
    from_crs : Any
        Pyproj.CRS or input required to create one
    to_crs : Any
        Pyproj.CRS or input required to create one
    geom : BaseGeometry
        Shapely geometry to be reprojected

    Returns
    -------
    BaseGeometry
        Reprojected geometry
    """
    tf = pyproj.Transformer.from_crs(from_crs, to_crs, always_xy=True)
    return transform(tf.transform, geom)
