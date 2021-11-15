from pathlib import Path
from typing import List

import typer

from arcpy2foss.extent import extents_to_features

app = typer.Typer()


@app.command()
def hello_world():
    typer.echo("Hello world")


@app.command()
def datasets_to_extent(input_files: List[Path], output_file: Path, output_format: str = "GeoJSON"):
    return extents_to_features(input_files=input_files, output_file=output_file, output_format=output_format)
