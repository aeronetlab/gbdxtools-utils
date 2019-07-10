import shapely
import shapely.geometry


class AreaOfInterest:

    def __init__(
            self,
            bbox: tuple = None,
            wkt: str = None,
            geojson: dict = None,
    ):
        if bbox is not None:
            self._shape = shapely.geometry.box(*bbox)
        elif wkt is not None:
            self._shape = shapely.wkt.loads(wkt)
        elif geojson is not None:
            self._shape = shapely.geometry.shape(geojson)
        else:
            raise ValueError('Please provide one of `bbox`, `wkt`, `geojson` geometries')

    @property
    def wkt(self) -> str:
        "Return geometry in WKT string format"
        return self._shape.wkt

    @property
    def geojson(self) -> dict:
        """Return geojson-like geometry"""
        return shapely.geometry.mapping(self._shape)

    @property
    def bbox(self) -> tuple:
        """Return bounds tuple (xmin, ymin, xmax, ymax)"""
        return self._shape.bounds
