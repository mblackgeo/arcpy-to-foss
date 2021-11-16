import os
from modulefinder import Module
from pathlib import Path
from typing import Iterable

import fiona
import geopandas as gpd
import pyproj
import rasterio
from fiona.errors import DriverError
from rasterio.errors import RasterioIOError
from shapely.geometry import Polygon, box

from arcpy2foss.utils import reproject


def extent_from_file(filename: Path, as_wgs84: bool = True, lib: Module = fiona) -> Polygon:
    """Get the spatial extent from a file

    Parameters
    ----------
    filename : Path
        Path of file
    as_wgs84 : bool, optional
        Return extent in WGS84, by default True
    lib : Module
        The library use to open the file, e.g. fiona, rasterio

    Returns
    -------
    Polygon
        Bounding box extent
    """
    with lib.open(filename) as src:
        bounds = box(*src.bounds)
        prj = pyproj.CRS.from_user_input(src.crs)
        epsg_code = prj.to_epsg(min_confidence=20)

    if as_wgs84 and epsg_code != 4326:
        bounds = reproject(from_crs=prj, to_crs="EPSG:4326", geom=bounds)

    return bounds


def get_extent(filename: Path, as_wgs84: bool = True) -> Polygon:
    """Get the bounding box extent from a file

    Parameters
    ----------
    filename : Path
        Path to raster or vector file
    as_wgs84 : bool, optional
        Return the Polygonal extent in the WGS84 CRS, by default True

    Returns
    -------
    Polygon
        A bounding box extent of the data in ``filename``
    """
    try:
        return extent_from_file(filename, as_wgs84=as_wgs84, lib=fiona)
    except DriverError:
        pass

    try:
        return extent_from_file(filename, as_wgs84=as_wgs84, lib=rasterio)
    except RasterioIOError:
        pass

    # raise if neither OGR or GDAL can read the data
    raise NotImplementedError(f"Could not open file as either raster or vector: {filename}")


def extents_to_features(input_files: Iterable[Path], output_file: Path, output_format: str = "GeoJSON") -> None:
    """Create a new vector file that contains the bounding box extents of each
    given file in ``input_files``.

    Parameters
    ----------
    input_files : Iterable[Path]
        List of input fiels (raster or vector)
    output_file : Path
        Path to output file (vector) that will be created with the bounding
        boxes of each file from ``input_files``. This will be in WGS84.
        The CRS will be WGS-84.
    output_format : str
        The output format (or Driver) to use when writing ``output_file``.
        See also `fiona.support_drivers`.
    """
    extents = []
    for fn in input_files:
        extents.append({"filename": os.path.basename(fn), "geometry": get_extent(fn, as_wgs84=True)})

    out = gpd.GeoDataFrame(extents, geometry="geometry", crs="EPSG:4326")
    out.to_file(output_file, driver=output_format)
