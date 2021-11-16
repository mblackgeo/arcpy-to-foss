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
    # Find matches from the right gdf that are within the max distance
    right_matches = right.sjoin_nearest(
        left,
        lsuffix="keep",
        rsuffix="drop",
        how="left",
        max_distance=max_distance,
        distance_col=distance_col,
    )

    # remove any duplicate columns (i.e. columns that were added from the left gdf)
    cols_to_drop = [c for c in right_matches.columns if c.endswith("_drop")]
    right_matches = right_matches.drop(columns=cols_to_drop).dropna(subset=[distance_col])

    # rename the suffixed columns that should be kept (i.e. the original columns in the right gdf)
    col_rename_map = {c: c.replace("_keep", "") for c in right_matches.columns if c.endswith("_keep")}
    right_matches = right_matches.rename(columns=col_rename_map)

    # Additional filter based on matching values of specific columns if any are specified
    # This is a standard pandas join that does not use geometry
    if match_cols:
        right_matches = right_matches.merge(left[match_cols], how="inner", on=match_cols)

    return right_matches
