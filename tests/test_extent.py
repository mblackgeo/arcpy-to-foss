import os
from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import box

from arcpy2foss.extent import extents_to_features, get_extent


def test_get_extent_vector_wgs84(resources_dir: str):
    # Vector already in EPSG:4326
    fn = os.path.join(resources_dir, "vector.geojson")
    result = get_extent(fn, as_wgs84=True)
    expected = box(9.94, 53.53, 9.95, 53.54)
    assert result.almost_equals(expected, decimal=2)


def test_get_extent_vector_non_wgs84(resources_dir: str):
    # Vector in EPSG:32632
    fn = os.path.join(resources_dir, "vector_epsg32632.gpkg")
    result = get_extent(fn, as_wgs84=True)
    expected = box(9.94, 53.53, 9.95, 53.54)
    assert result.almost_equals(expected, decimal=2)


def test_get_extent_raster_wgs84(resources_dir: str):
    # Raster already in EPSG:4326
    fn = os.path.join(resources_dir, "oneband.tif")
    result = get_extent(fn, as_wgs84=True)
    expected = box(9.93, 53.53, 9.96, 53.54)
    assert result.almost_equals(expected, decimal=2)


def test_get_extent_raster_non_wgs84(resources_dir: str):
    # Raster in EPSG:32632, extent should be converted to WGS84
    fn = os.path.join(resources_dir, "raster.tif")
    result = get_extent(fn, as_wgs84=True)
    expected = box(9.93, 53.53, 9.96, 53.54)
    assert result.almost_equals(expected, decimal=2)


def test_get_extent_invalid_file(resources_dir: str):
    with pytest.raises(NotImplementedError):
        get_extent(os.path.join(resources_dir, "asdasd"))


def test_extents_to_features(resources_dir: str, tmp_path: Path):
    files = [os.path.join(resources_dir, f) for f in ["raster.tif", "vector.geojson"]]
    out_fn = tmp_path / "test.geojson"

    extents_to_features(files, out_fn, output_format="GeoJSON")
    assert os.path.exists(out_fn)

    out = gpd.read_file(out_fn)
    assert "raster.tif" in out.filename.tolist()
    assert "vector.geojson" in out.filename.tolist()
