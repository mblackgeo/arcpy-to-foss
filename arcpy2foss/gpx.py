from pathlib import Path
from typing import Iterable

import geopandas as gpd
import gpxpy.gpx
from shapely.geometry import LineString


def check_geometry(
    gdf: gpd.GeoDataFrame,
    valid_geom_types: Iterable[str] = ("Point", "LineString"),
    n_unique_geoms: int = 1,
) -> None:
    """Check that a GeoDataFrame contains specific geometry types

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        DataFrame to check
    valid_geom_types : Iterable[BaseGeometry], optional
        Types of geometry that considered valid, by default ("Point", "LineString")
    n_unique_geoms : int, optional
        Number of unique geometry types allowed (from ``valid_geom_types``), by default 1

    Raises
    ------
    ValueError
        If there are more than ``n_unique_geoms``
    ValueError
        If there are geometry types that are not in ``valid_geom_types``
    """
    geom_types = set(gdf.geometry.type.unique())

    # raise if there are more unique types of geometry than allowed
    if len(geom_types) > n_unique_geoms:
        raise ValueError(f"Too many geometry types : got {len(geom_types)}, allowed {n_unique_geoms}")

    # raise if there are geometry types that are not valid
    invalid_geoms = geom_types - set(valid_geom_types)
    if invalid_geoms:
        raise ValueError(f"Invalid geometry type(s) : {invalid_geoms} (allowed : {valid_geom_types})")


def points_to_line(gdf: gpd.GeoDataFrame, groupby: Iterable[str]) -> gpd.GeoDataFrame:
    """Convert Points to a LineString in a GeoDataFrame

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing points
    groupby : Iterable[str]
        Column(s) to group by

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with Points converted to LineString
    """
    return gdf.groupby(groupby).agg({"geometry": lambda x: LineString(list(x))}).reset_index()


def linestring_to_gpx(gdf: gpd.GeoDataFrame, output_file: Path) -> None:
    """Write a GeoDataFrame of LineString geometry to GPX file

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing LineStrings.
        Each row (i.e. LineString) will be a new Track in the GPX file.
    output_file : Path
        GPX file to be created.
    """
    gpx = gpxpy.gpx.GPX()

    # Add a new track for each LineString geometry in the data
    for geom in gdf.geometry.to_list():
        # Create track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        # Create first segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Add the points to the segment
        for pnt in list(geom.coords):
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(pnt[1], pnt[0]))

    # Write the XML to file
    with open(output_file, "w") as file:
        file.write(gpx.to_xml())


def write_gpx(gdf: gpd.GeoDataFrame, output_file: Path) -> None:
    """Write a GeoDataFrame to an XML GPX file (using `gpxpy` or `fiona`)

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame to write.
        Point geometry will be converted to waypoints.
        LineStrings will be converted to tracks.
    output_file : Path
        Output file path.
    """
    # If we only have points then we can just get geopandas/fiona to write it out
    if "Point" in gdf.geometry.type.unique():
        gdf.to_file(output_file, driver="GPX")

    # If we have LineString then we need to manually create the tracks and use
    # gpxpy to write it out
    if "LineString" in gdf.geometry.type.unique():
        linestring_to_gpx(gdf, output_file)

    else:
        NotImplementedError(f"GPX writing not implemented for geometry type(s) : {gdf.geometry.type.unique()}")


def to_gpx(input_file: Path, output_file: Path) -> None:
    """Convert an input vector file to a GPX file

    Parameters
    ----------
    input_file : Path
        Input vector file, must be readable by OGR.
        Can contain either Point or LineString geometry.
        Points will be converted to Waypoint features and LineString to tracks.
    output_file : Path
        Path to output GPX file that will be created
    """
    src_gdf = gpd.read_file(input_file)

    # Input must contain only one type of geometry (Point or LineString)
    check_geometry(src_gdf)

    # Ensure output gdf is in WGS84
    out = src_gdf.to_crs(crs=4326)

    # If there is a "Type" field with value TRKPT and geometry of points
    # make them into a LineString (i.e. convert to TRKS in the GPX output)
    if "Type" in src_gdf.columns:
        unique_types = src_gdf["Type"].unique()
        if len(unique_types) == 1 and unique_types[0] == "TRKPT":
            out = points_to_line(out, groupby=["Type"])

    # Save as GPX
    write_gpx(gdf=out, output_file=output_file)
