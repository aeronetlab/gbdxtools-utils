import shapely
import gbdxtools
import datetime as dt

from typing import List

from . import aoi

GBDX_SATELLITES = (
    'WORLDVIEW01',
    'WORLDVIEW02',
    'WORLDVIEW03_VNIR',
    'WORLDVIEW03_SWIR',
    'WORLDVIEW04',
    'GEOEYE01',
    'QUICKBIRD02',
    'LANDSAT',
)


# ---------------------------------------------
#    GBDX platform filters
# ---------------------------------------------

def _satellite_filter(satellites: tuple = GBDX_SATELLITES) -> tuple:
    filter = '({})'.format(
        ' OR '.join(
            ['sensorPlatformName = "{}"'.format(s) for s in satellites]
        )
    )
    return tuple([filter])


def _cloud_filter(max_cloud_cover: int = 0, min_cloud_cover: int = None) -> tuple:
    filters = []
    if max_cloud_cover is not None:
        filters.append('cloudCover <= {}'.format(max_cloud_cover))
    if min_cloud_cover is not None:
        filters.append('cloudCover >= {}'.format(min_cloud_cover))

    return tuple(filters)


def _offnadir_angle_filter(max_offnadir_angle: float = 45., min_offnadir_angle: float = 0) -> tuple:
    filters = []
    if max_offnadir_angle is not None:
        filters.append('offNadirAngle <= {}'.format(max_offnadir_angle))
    if min_offnadir_angle is not None:
        filters.append('offNadirAngle >= {}'.format(min_offnadir_angle))

    return tuple(filters)


# ---------------------------------------------
#    Helper functions
# ---------------------------------------------

def _to_date(date):
    if date is None:
        return date

    if isinstance(date, (tuple, list)):
        date = dt.date(*date)

    date_str = '{yyyy}-{mm:02}-{dd:02}T00:00:00.000Z'.format(
        yyyy=date.year,
        mm=date.month,
        dd=date.day
    )
    return date_str


def filter_by_coverage(search_results: list, geometry: dict) -> list:
    """

    Args:
        search_results: list of gbdxtools.search result
        geometry: geometry in geojson format

    Returns:
        filtered_results
    """

    # convert results images footprints to shapely geometry
    footrprints_wkt = [result['properties']['footprintWkt'] for result in search_results]
    footprints = [shapely.wkt.loads(footprint_wkt) for footprint_wkt in footrprints_wkt]

    # convert area of interests geometry to shapely geometry
    geometry = shapely.geometry.shape(geometry)
    geometry_box = shapely.geometry.box(*geometry.bounds)

    filtered_results = ([search_results[i] for i in range(len(search_results))
                         if footprints[i].contains(geometry_box)])

    return filtered_results


# ---------------------------------------------
#    GBDX searcher class
# ---------------------------------------------

class GBDXSearcher:

    def __init__(self,
                 satellites=GBDX_SATELLITES,
                 types=None,
                 max_cloud_cover=100,
                 min_off_nadir_angle=0,
                 max_off_nadir_angle=60,
                 start_date=None,
                 end_date=None,
                 filters=None):
        self.satellites = satellites
        self.types = types
        self.max_cloud_cover = max_cloud_cover
        self.min_off_nadir_angle = min_off_nadir_angle
        self.max_off_nadir_angle = max_off_nadir_angle
        self.start_date = start_date
        self.end_date = end_date
        self.filters = filters or []

        self.gbdx = gbdxtools.Interface()

    def collect_filters(self) -> tuple:
        filters = (
            *_satellite_filter(satellites=self.satellites),
            *_cloud_filter(max_cloud_cover=self.max_cloud_cover),
            *_offnadir_angle_filter(min_offnadir_angle=self.min_off_nadir_angle,
                                    max_offnadir_angle=self.max_off_nadir_angle),
            *self.filters,
        )

        return filters

    def get_search_params(self) -> dict:
        params = {
            'filters': self.collect_filters(),
            'startDate': _to_date(self.start_date),
            'endDate': _to_date(self.end_date),
            'types': self.types,
        }

        return params

    def get(
            self,
            aoi: aoi.AreaOfInterest
    ) -> List[dict]:
        params = self.get_search_params()
        search_results = self.gbdx.catalog.search(searchAreaWkt=aoi.wkt, **params)

        return search_results
