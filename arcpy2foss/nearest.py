from functools import reduce
from pathlib import Path
from typing import Iterable, Optional

import geopandas as gpd


def nearest_conditional_match_gdf(
    left: gpd.GeoDataFrame,
    right: gpd.GeoDataFrame,
    distance_col: str = "distance",
    match_cols: Optional[Iterable[str]] = None,
    max_distance: Optional[float] = None,
) -> gpd.GeoDataFrame:
    """Return rows from ``right`` that are within max_distance and match
    specific columns of ``left``.

    This function will find all the rows in the ``right`` GeoDataFrame that are
    within the given ``max_distance`` of the geometries in ``left`` as well as
    being able to conditionally join on any additional columns; i.e. rows are
    returned from ``right`` if they are within the given ``max_distance`` AND
    they also match the values in the specified ``match_cols``.

    Parameters
    ----------
    left : gpd.GeoDataFrame
        Left GeoDataFrame, should be same CRS as ``right``
    right : gpd.GeoDataFrame
        Right GeoDataFrame, should be same CRS as ``left``
    distance_col : str, optional
        Column to store the distances, by default "distance".
        Units will the same as the CRS.
    match_cols : Optional[Iterable[str]], optional
        Optional list of extra columns to match, by default None.
        These columns must exist in both ``left`` and ``right``.
    max_distance : Optional[float], optional
        Maximum distance for the spatial join, by default None.
        Units are the same as the CRS so care should be taken if geographic
        coordinate systems are used.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame containing the matching rows from ``right``.
    """
    # Use the spatial index to join all of the "right" rows and calculate their
    # distance with the "left" rows. Note that this needs to be a right join to
    # include all matches with "left", however this loses the left geometry col
    # which is added again below
    matches = left.sjoin_nearest(
        right,
        lsuffix="left",
        rsuffix="right",
        how="right",
        max_distance=max_distance,
        distance_col=distance_col,
    )

    # If max_distance was set, because we did a right join there will still
    # be rows present from in output that were greater than max distance
    # however their distance value will be NaN so we can safely drop them
    matches = matches.dropna(subset=[distance_col])

    # remove the suffix from the left columns
    col_rename_map = {c: c.replace("_left", "") for c in matches.columns}
    matches = matches.rename(columns=col_rename_map)

    # Add the "left" geometry back to the DataFrame
    matches = matches.rename(columns={"geometry": "geometry_right"})
    matches = matches.merge(left[["geometry"]].reset_index(), how="left", on=["index"])

    # Additional filter based on matching equality of specific columns
    # The matches DataFrame has the left and right columns (suffixed "_right")
    # so we can just apply a boolean filter on these
    if match_cols:
        mask = reduce(lambda a, b: a & b, [matches[f"{c}"] == matches[f"{c}_right"] for c in match_cols])
        matches = matches[mask].copy()

    return matches


def nearest_conditional_match(
    left_vector_file: Path,
    right_vector_file: Path,
    output_file: Path,
    output_format: str = "GeoJSON",
    distance_col: str = "distance",
    match_cols: Optional[Iterable[str]] = None,
    max_distance: Optional[float] = None,
) -> None:
    """Find rows from the right vector file that match left based on given criteria

    Parameters
    ----------
    left_vector_file : Path
        Path to "left" vector dataset. Must be readable by OGR.
        Should be the same CRS as right.
    right_vector_file : Path
        Path to "right" vector dataset. Must be readable by OGR.
        Should be same CRS as right
    output_file : Path
        Path to output file (vector) that will be created with the matching
        data from the ``right`` dataset.
    output_format : str
        The output format (or Driver) to use when writing ``output_file``.
        See also `fiona.support_drivers`.
    distance_col : str, optional
        Column to store the distances, by default "distance".
        Units will the same as the CRS.
    match_cols : Optional[Iterable[str]], optional
        Optional list of extra columns to match, by default None.
        These columns must exist in both ``left`` and ``right``.
    max_distance : Optional[float], optional
        Maximum distance for the spatial join, by default None.
        Units are the same as the CRS so care should be taken if geographic
        coordinate systems are used.
    """
    nearest_conditional_match_gdf(
        left=gpd.read_file(left_vector_file),
        right=gpd.read_file(right_vector_file),
        distance_col=distance_col,
        match_cols=match_cols,
        max_distance=max_distance,
    ).to_file(output_file, driver=output_format)
