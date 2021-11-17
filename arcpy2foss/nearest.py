from functools import reduce
from typing import Iterable, Optional

import geopandas as gpd


def conditional_sjoin(
    left: gpd.GeoDataFrame,
    right: gpd.GeoDataFrame,
    distance_col: str = "distance",
    max_distance: Optional[float] = None,
    join_on: Optional[Iterable[str]] = None,
) -> gpd.GeoDataFrame:
    """Conditional spatial join with optional distance and join columns

    This performs a "left" join with additional optional constraints based on
    the distance between between features and/or joining on specific columns.

    Parameters
    ----------
    left : gpd.GeoDataFrame
        Left GeoDataFrame, should be same CRS as ``right``
    right : gpd.GeoDataFrame
        Right GeoDataFrame, should be same CRS as ``left``
    distance_col : str
        Column to store the distances, by default "distance".
        Units will the same as the CRS of the source data.
    max_distance : Optional[float], optional
        Maximum distance for the spatial join, by default None.
        Units are the same as the CRS so care should be taken if geographic
        coordinate systems are used.
    join_on : Optional[Iterable[str]], optional
        Optional list of extra columns to join on, by default None.
        These columns must exist in both ``left`` and ``right``.

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
    if join_on:
        mask = reduce(lambda a, b: a & b, [matches[f"{c}"] == matches[f"{c}_right"] for c in join_on])
        matches = matches[mask].copy()

    return matches
