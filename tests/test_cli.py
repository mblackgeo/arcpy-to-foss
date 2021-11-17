import os
from pathlib import Path

from typer.testing import CliRunner

from arcpy2foss.cli import app

runner = CliRunner()


def test_cli_conditional_spatial_join(resources_dir: str, tmp_path: Path):
    left_file = os.path.join(resources_dir, "sjoin_left.geojson")
    right_file = os.path.join(resources_dir, "sjoin_right.geojson")
    out_fn = tmp_path / "test.geojson"

    args = ["conditional-spatial-join", "--left", left_file, "--right", right_file, "--output-file", str(out_fn)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert os.path.exists(out_fn)


def test_cli_datasets_to_extent(resources_dir: str, tmp_path: Path):
    files = [os.path.join(resources_dir, f) for f in ["raster.tif", "vector.geojson"]]
    out_fn = tmp_path / "test.geojson"

    args = ["datasets-to-extent", *files, "--output-file", str(out_fn)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert os.path.exists(out_fn)


def test_cli_vector_to_gpx(resources_dir: str, tmp_path: Path):
    fn = os.path.join(resources_dir, "points_as_track_epsg32630.gpkg")
    out_fn = tmp_path / "test.gpx"

    args = ["vector-to-gpx", fn, str(out_fn)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert os.path.exists(out_fn)
