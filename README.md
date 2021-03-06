# ArcPy to FOSS
Conversion of ArcPy scripts to free and open-source software (FOSS).

The code in this repository is converted from [ESRI's ArcPy examples repository](https://github.com/arcpy/sample-gp-tools). No attempts have been made to convert the "toolbox" versions, only the scripts have been converted, however these could easily be converted to QGIS processing tools if needed; this may be tackled in the future.

## Installation

A valid GDAL/OGR installation is required, this can be achieved using your package manager of choice (e.g. apt, brew, conda etc.). Once this is installed, clone the repository and install with pip:

```shell
git clone git@github.com:mblackgeo/arcpy-to-foss.git
cd arcpy-to-foss
pip install .
```

## Usage

A number of scripts will be available at the CLI or can be imported for use in python. The CLI tools can be accessed after installing the package with:

```shell
a2f --help
```

Currently converted tools include:

* [`datasets-to-extent`](arcpy2foss/extent.py) is a conversion of [DatasetExtentToFeatures](https://github.com/arcpy/sample-gp-tools/tree/master/DatasetExtentToFeatures).
    * This takes any number of raster and vector sources as input and outputs a single vector (GeoJSON by default) containing the bounding box of each dataset
    * The output will always be in WGS-84 however any supported OGR format can be used (e.g. GeoPackage, GeoJSON, shapefile etc.)
* [`vector-to-gpx`](arcpy2foss/gpx.py) is a conversion of [FeaturesToGPX](https://github.com/arcpy/sample-gp-tools/tree/master/FeaturesToGPX).
    * Takes a vector input file with either Point or LineString data and converts it to GPX (waypoints or tracks, respectively).
    * If the input vector contains Points geometry and a `Type` field with the value `TRKPT` it will be converted to a track instead of waypoints.
* [`conditional-sjoin`](arcpy2foss/sjoin.py) is a conversion of [NearByGroup](https://github.com/arcpy/sample-gp-tools/tree/master/NearByGroup).
    * Effectively performs a "left" spatial join with constraints by max distance and/or additional join columns

## Development

A valid GDAL/OGR installation is required, this can be achieved using your package manager of choice (e.g. apt, conda). Once this is installed, set up a new clean virtual environment and install the requirements:

```shell
# install gdal, e.g.
# apt install libgdal-dev
# conda install gdal -c conda-forge

# create new virtualenv and install reqs
mkvirtualenv --python=/usr/bin/python3.8 arcpy2foss
pip install -r requirements-dev.txt
pip install -e .
pre-commit install
```

* [Pytest](https://docs.pytest.org/en/6.2.x/) is used for the functional tests of the application (see [`/tests`](tests/)).
* Code is linted using [flake8](https://flake8.pycqa.org/en/latest/) with `--max-line-length=120`
* Code formatting is validated using [Black](https://github.com/psf/black)
* [pre-commit](https://pre-commit.com/) is used to run these checks locally before files are pushed to git
* The [Github Actions pipeline](.github/workflows/pipeline.yml) also runs these checks and tests
