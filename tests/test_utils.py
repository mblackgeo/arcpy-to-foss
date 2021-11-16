import pytest
from shapely.geometry import Point

from arcpy2foss.utils import reproject


def test_reproject():
    from_crs = "EPSG:32632"  # UTM 32N
    to_crs = "EPSG:4326"  # WGS84

    # UTM point (Easting, Northing)
    pnt = Point(510500, 7042500)

    # WGS conversion (lng, lat)
    expected = Point(9.21, 64.51)

    out = reproject(from_crs=from_crs, to_crs=to_crs, geom=pnt)

    assert pytest.approx(out.x, rel=1e-1) == expected.x
    assert pytest.approx(out.y, rel=1e-1) == expected.y
