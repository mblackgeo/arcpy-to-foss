from pathlib import Path
from typing import List

import typer

from arcpy2foss.extent import extents_to_features
from arcpy2foss.gpx import to_gpx

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
