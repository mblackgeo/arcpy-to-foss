import os
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import MultiLineString

from arcpy2foss.gpx import to_gpx


def test_to_gpx_points(resources_dir: str, tmp_path: Path):
    # Vector in UTM 30N
    fn = os.path.join(resources_dir, "points_epsg32630.gpkg")
    out_fn = tmp_path / "test.gpx"

    to_gpx(input_file=fn, output_file=out_fn)
    assert os.path.exists(out_fn)

    out = gpd.read_file(out_fn)
    assert isinstance(out, gpd.GeoDataFrame) is True
    assert len(out) == 4
    assert len(out.columns) == 24

    # check the coordinates of the first point are correct
    lat, lon = (54.58825, -1.18912)
    first_pnt = out.geometry.iloc[0]
    assert pytest.approx(first_pnt.y, rel=1e-5) == lat
    assert pytest.approx(first_pnt.x, rel=1e-5) == lon


def test_to_gpx_points_to_track(resources_dir: str, tmp_path: Path):
    # Vector in UTM 30N
    fn = os.path.join(resources_dir, "points_as_track_epsg32630.gpkg")
    out_fn = tmp_path / "test.gpx"

    to_gpx(input_file=fn, output_file=out_fn)
    assert os.path.exists(out_fn)

    out = gpd.read_file(out_fn, layer="tracks")
    assert isinstance(out, gpd.GeoDataFrame) is True
    assert len(out) == 1
    assert isinstance(out.geometry.iloc[0], MultiLineString) is True
