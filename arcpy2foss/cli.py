from pathlib import Path
from typing import List, Optional

import typer

from arcpy2foss.extent import extents_to_features
from arcpy2foss.gpx import to_gpx
from arcpy2foss.nearest import nearest_conditional_match as ncm

app = typer.Typer()


@app.command()
def datasets_to_extent(
    input_files: List[Path] = typer.Argument(default=None, help="List of 1 or more raster and/or vector datasets"),
    output_file: Path = typer.Argument(default=None, help="Path to output vector file"),
    output_format: str = typer.Argument(default="GeoJSON", help="Output vector file format"),
):
    """
    Create vector of dataset extents.

    The output file will always be in WGS-84 projection, however the format can
    be specified, by default is GeoJSON.
    """
    return extents_to_features(input_files=input_files, output_file=output_file, output_format=output_format)


@app.command()
def vector_to_gpx(
    input_file: Path = typer.Argument(default=None, help="Input vector file to convert to GPX"),
    output_file: Path = typer.Argument(default=None, help="Ouput path for GPX file"),
):
    """
    Convert a vector file to GPX.

    Point data is converted to WayPoints and LineString to Tracks. If there is
    a "Type" field with value TRKPT and Point geometry, then a Track will be
    created.
    """
    return to_gpx(input_file=input_file, output_file=output_file)


@app.command()
def nearest_conditional_match(
    left_vector_file: Path = typer.Argument(default=None, help="Source vector file"),
    right_vector_file: Path = typer.Argument(default=None, help="Vector file to match with source"),
    output_file: Path = typer.Argument(default=None, help="Path to output vector file"),
    output_format: str = typer.Argument(default="GeoJSON", help="Output vector file format"),
    distance_col: str = typer.Argument(default="distance", help="Name of field to store distance"),
    match_cols: Optional[List[str]] = typer.Argument(default=None, help="Fields to match, must be in both datasets"),
    max_distance: Optional[float] = typer.Argument(default=None, help="Distance threshold in same units as vector CRS"),
):
    """
    Match rows from ``right`` that are within max_distance and match specific columns of ``left``.

    This function will find all the rows in the ``right`` dataset that are
    within the given ``max_distance`` of the geometries in ``left`` as well as
    being able to conditionally join on any additional columns; i.e. rows are
    returned from ``right`` if they are within the given ``max_distance`` AND
    they also match the values in the specified ``match_cols``.
    """
    return ncm(
        left_vector_file=left_vector_file,
        right_vector_file=right_vector_file,
        output_file=output_file,
        output_format=output_format,
        distance_col=distance_col,
        match_cols=match_cols,
        max_distance=max_distance,
    )
