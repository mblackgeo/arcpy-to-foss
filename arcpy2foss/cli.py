from typing import List, Optional

import geopandas as gpd
import typer
from shapely import wkt

from arcpy2foss.extent import extents_to_features
from arcpy2foss.gpx import to_gpx
from arcpy2foss.sjoin import conditional_sjoin

app = typer.Typer()


@app.command()
def datasets_to_extent(
    input_files: List[str] = typer.Argument(..., help="List of 1 or more raster and/or vector datasets"),
    output_file: str = typer.Option(..., help="Path to output vector file"),
    output_format: str = typer.Option(default="GeoJSON", help="Output vector file format"),
):
    """
    Create vector of dataset extents.

    The output file will always be in WGS-84 projection, however the format can
    be specified, by default is GeoJSON.
    """
    return extents_to_features(input_files=input_files, output_file=output_file, output_format=output_format)


@app.command()
def vector_to_gpx(
    input_file: str = typer.Argument(..., help="Input vector file to convert to GPX"),
    output_file: str = typer.Argument(..., help="Ouput path for GPX file"),
):
    """
    Convert a vector file to GPX.

    Point data is converted to WayPoints and LineString to Tracks. If there is
    a "Type" field with value TRKPT and Point geometry, then a Track will be
    created.
    """
    return to_gpx(input_file=input_file, output_file=output_file)


@app.command()
def conditional_spatial_join(
    left: str = typer.Option(..., help="Source vector file"),
    right: str = typer.Option(..., help="Vector file to match with source"),
    output_file: str = typer.Option(..., help="Path to output vector file"),
    output_format: str = typer.Option(default="GeoJSON", help="Output vector file format"),
    distance_col: Optional[str] = typer.Option(default="distance", help="Name of field to store distance"),
    join_on: Optional[List[str]] = typer.Option(default=None, help="Attributes to match, must be in both datasets"),
    max_distance: Optional[float] = typer.Option(default=None, help="Distance threshold in same units as vector CRS"),
):
    """
    Conditional spatial join between left/right based on distance and/or attributes

    This function will perform a "left" spatial join matching rows from "right"
    that are within the specified conditions. This can be based on a max_distance
    value (same units as the CRS of the input data) and/or joining on one or more
    attributes of the data (attributes must be in both left/right).
    """
    out = conditional_sjoin(
        left=gpd.read_file(left),
        right=gpd.read_file(right),
        distance_col=distance_col,
        join_on=join_on,
        max_distance=max_distance,
    )

    # convert the geometry_right to WKT to allow it to be written to file
    out["geometry_right"] = out.geometry_right.apply(wkt.dumps)
    out.to_file(output_file, driver=output_format)
