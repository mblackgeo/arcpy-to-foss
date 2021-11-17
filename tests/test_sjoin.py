import os

import geopandas as gpd
import pytest

from arcpy2foss.sjoin import conditional_sjoin


@pytest.fixture
def gdf1(resources_dir: str):
    return gpd.read_file(os.path.join(resources_dir, "sjoin_left.geojson"))


@pytest.fixture
def gdf2(resources_dir: str):
    return gpd.read_file(os.path.join(resources_dir, "sjoin_right.geojson"))


def test_nearest_conditional_match_gdf(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # No conditions, just returns all of the "right" DF with a distance column
    out = conditional_sjoin(left=gdf1, right=gdf2)
    assert len(out) == 2
    assert "distance" in out.columns
    assert ["river_tees", "hartlepool"] == out.id_right.tolist()


def test_nearest_conditional_match_gdf_with_max_distance(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # Only 1 should be returned that is within the distance
    out = conditional_sjoin(left=gdf1, right=gdf2, max_distance=0.05)
    assert len(out) == 1
    assert out.id_right.iloc[0] == "river_tees"


def test_nearest_conditional_match_gdf_with_match_cols(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # Both rows will match as there is no distance specified
    # however only 1 row will match based on using "match_cols"
    out = conditional_sjoin(left=gdf1, right=gdf2, join_on=["col1"])
    assert len(out) == 1
    assert out.id_right.iloc[0] == "hartlepool"


def test_nearest_conditional_match_gdf_with_match_cols_and_distance(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # There are no matches within the distance and having the same values
    # in col1 and col2
    out = conditional_sjoin(left=gdf1, right=gdf2, join_on=["col1", "col2"], max_distance=0.1)
    assert len(out) == 0
