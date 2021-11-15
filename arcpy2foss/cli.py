from pathlib import Path
from typing import List

import typer

from arcpy2foss.extent import extents_to_features

app = typer.Typer()


@app.command()
def hello_world():
    typer.echo("Hello world")


@app.command()
def datasets_to_extent(
    input_files: List[Path] = typer.Argument(default=None, help="List of 1 or more raster and/or vector datasets"),
    output_file: Path = typer.Argument(default=None, help="Path to output vector file"),
    output_format: str = typer.Argument(default="GeoJSON", help="Output vector file format"),
):
    return extents_to_features(input_files=input_files, output_file=output_file, output_format=output_format)
