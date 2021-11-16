from typing import Iterable, Optional

import geopandas as gpd


def nearest_match(
    left: gpd.GeoDataFrame,
    right: gpd.GeoDataFrame,
    distance_col: str = "distance",
    match_cols: Optional[Iterable[str]] = None,
    max_distance: Optional[float] = None,
):
    # Find matches from the right gdf that are within the max distance
    right_matches = right.sjoin_nearest(
        left,
        lsuffix="keep",
        rsuffix="drop",
        how="left",
        max_distance=max_distance,
        distance_col=distance_col,
    )

    # remove any duplicate columns
    cols_to_drop = [c for c in right_matches.columns if c.endswith("_drop")]
    right_matches = right_matches.drop(columns=cols_to_drop).dropna(subset=[distance_col])

    # rename the suffixed columns that should be kept
    col_rename_map = {c: c.replace("_keep", "") for c in right_matches.columns if c.endswith("_keep")}
    right_matches = right_matches.rename(columns=col_rename_map)

    # Additional filter based on matching values of specific columns
    if match_cols:
        right_matches = right_matches.merge(left[match_cols], how="inner", on=match_cols)

    return right_matches
