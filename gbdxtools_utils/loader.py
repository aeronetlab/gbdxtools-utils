import os
import json
import geojson
import shapely
import gbdxtools
import expiringdict

from typing import Union

from . import aoi
from . import enums
from . import errors


class ImageryLoader:
    """Load imagery and its meta and save on disk, store all fetched imagery to cache.
    Args:
        cache_image_expiration_time (int): time in seconds to cache fetched image
        **image_params: image fetching parameters (pansharpen, dra, dtype, acomp, bands)
    """
    IMAGE_NAME = 'orthophoto.tif'
    META_NAME = 'meta.geojson'

    def __init__(
            self,
            cache_image_expiration_time: int = 3600,
            **image_params,
    ):
        self._gbdx = gbdxtools.Interface()
        self._image_params = image_params
        self._catalog_image_cache = expiringdict.ExpiringDict(
            max_len=1000,
            max_age_seconds=cache_image_expiration_time,
        )
        self._not_in_catalog_image_cache = set()

    def _request_image(self, image_id: str) -> gbdxtools.CatalogImage:
        try:
            image = self._gbdx.catalog_image(cat_id=image_id, **self._image_params)
        except Exception as e:
            if errors.NotInCatalogError.catch(e):
                raise errors.NotInCatalogError(str(e))
            else:
                raise e
        return image

    def _update_cache(
            self,
            image_id: str,
            image: gbdxtools.CatalogImage
    ):
        if image is not None:
            self._catalog_image_cache[image_id] = image
        else:
            self._not_in_catalog_image_cache.add(image_id)

    def _get_image(
            self,
            image_id: str,
            use_cache: bool = True,
    ) -> Union[gbdxtools.CatalogImage, None]:

        if use_cache and (image_id in self._catalog_image_cache):
            image = self._catalog_image_cache[image_id]

        elif use_cache and (image_id in self._not_in_catalog_image_cache):
            image = None

        else:
            try:
                image = self._request_image(image_id)
            except errors.NotInCatalogError:
                image = None

        self._update_cache(image_id, image)

        return image

    def _compose_meta(
            self,
            image: gbdxtools.CatalogImage,
            aoi: aoi.AreaOfInterest = None,
    ) -> geojson.FeatureCollection:

        if aoi:
            geometry = aoi.geojson
        else:
            geometry = shapely.wkt.loads(image.metadata['imageBoundsWGS84'])

        properties = image.metadata['image']
        crs = image.metadata['georef']['spatialReferenceSystemCode']

        f = geojson.Feature(geometry=geometry, properties=properties)
        fc = geojson.FeatureCollection([f], crs=crs)

        return fc

    def _load_meta(
            self,
            image: gbdxtools.CatalogImage,
            path: str,
            aoi: aoi.AreaOfInterest = None,
    ):
        meta = self._compose_meta(image, aoi)
        with open(path, 'w') as f:
            json.dump(meta, f)

    def _load_image(
            self,
            image: gbdxtools.CatalogImage,
            path: str,
            aoi: aoi.AreaOfInterest = None,
            **kwargs
    ):
        try:
            if aoi is not None:
                image = image.aoi(bbox=aoi.bbox)
            image.geotiff(path=path, **kwargs)
        except Exception as e:
            if errors.ImageExpiredError.catch(e):
                raise errors.ImageExpiredError(str(e))
            else:
                raise e

    def load(
            self,
            image_id: str,
            path: str,
            aoi: aoi.AreaOfInterest = None,
            use_cache: bool = True,
            **load_kwargs,
    ):
        """Load imagery and its meta and save on disk

        Args:
            image_id (str): gbdx catalog image id
            path (str): direcotry to save `orthophoto.tif` and `meta.geojson` loaded files
            aoi (aoi.AreaOfInterest): area of interest
            use_cache (bool): - optional, use cached images or not
            **load_kwargs: additional gbdx `.geotiff` method params (e.g. spec='rgb')

        Returns:
            gbdxtools_utils.LoadStatus: loading status (success, fail, etc.)

        """

        image_path = os.path.join(path, self.IMAGE_NAME)
        meta_path = os.path.join(path, self.META_NAME)

        # fetch from cache if available
        image = self._get_image(image_id, use_cache=use_cache)

        if image is None:
            return enums.LoadStatus.NOT_IN_CATALOG

        try:
            self._load_image(image, image_path, aoi=aoi, **load_kwargs)
            self._load_meta(image, meta_path, aoi=aoi)
        except errors.ImageExpiredError:
            self.load(image_id, path, aoi, use_cache=False)

        return enums.LoadStatus.SUCCESS
