import geopandas as gpd
import pytest
from shapely.geometry import Point

from arcpy2foss.nearest import nearest_match


@pytest.fixture
def gdf1():
    return gpd.GeoDataFrame(
        [
            {
                "id": "riverside",
                "col1": "a",
                "col2": "b",
                "geometry": Point(-1.2168849741005956, 54.57827957221454795),
            },
        ],
        crs=4326,
    )


@pytest.fixture
def gdf2():
    return gpd.GeoDataFrame(
        [
            {
                "id": "river_tees",
                "col1": "z",
                "col2": "b",
                "geometry": Point(-1.21279327075493448, 54.58131930464433168),
            },
            {
                "id": "hartlepool",
                "col1": "a",
                "col2": "c",
                "geometry": Point(-1.20634573821025537, 54.68589717425042807),
            },
        ],
        crs=4326,
    )


def test_nearest_match(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # No conditions, just returns all of the "right" DF with a distance column
    out = nearest_match(left=gdf1, right=gdf2)
    assert len(out) == 2
    assert "distance" in out.columns


def test_nearest_match_with_max_distance(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # Only 1 should be returned that is within the distance
    out = nearest_match(left=gdf1, right=gdf2, max_distance=0.05)
    assert len(out) == 1
    assert out.id.iloc[0] == "river_tees"


def test_nearest_match_with_match_cols(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # Both rows will match as there is no distance specified
    # however only 1 row will match based on using "match_cols"
    out = nearest_match(left=gdf1, right=gdf2, match_cols=["col1"])
    assert len(out) == 1
    assert out.id.iloc[0] == "hartlepool"


def test_nearest_match_with_match_cols_and_distance(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame):
    # There are no matches within the distance and having the same values
    # in col1 and col2
    out = nearest_match(left=gdf1, right=gdf2, match_cols=["col1", "col2"], max_distance=0.1)
    assert len(out) == 0
