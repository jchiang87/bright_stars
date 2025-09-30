"""
Classes to wrap skycatalogs.StarObjects to enable their fluxes to
be increased by a delta magnitude value set in the yaml config.
"""
import galsim
from skycatalogs.objects import BaseObject, ObjectCollection
from skycatalogs.objects.star_object import StarObject

__all__ = ["BrighterStarsObject", "BrighterStarsCollection"]


class BrighterStarsObject(BaseObject):

    def __init__(self, star_object, delta_magnorm, parent_collection, index):
        self._belongs_to = parent_collection
        self._belongs_index = index
        self._id = "brighter_star_" + star_object.id
        self._ra = star_object.ra
        self._dec = star_object.dec
        self.star_object = star_object
        self.delta_magnorm = delta_magnorm

    def get_gsobject_components(self, gsparams=None, rng=None):
        if gsparams is not None:
            gsparams = galsim.GSParams(**gsparams)
        return {'this_object': galsim.DeltaFunction(gsparams=gsparams)}

    def get_observer_sed_component(self, component, mjd=None):
        if component != "this_object":
            raise RuntimeError("Unknown SED component: %s", component)
        sed = self.star_object.get_observer_sed_component(component, mjd=mjd)
        # Apply delta_magnorm
        sed *= 10.0**(-self.delta_magnorm/2.5)
        return sed


class BrighterStarsCollection(ObjectCollection):
    _object_type = "brighter_stars"

    def __init__(self, object_list, delta_magnorm):
        self._object_type_unique = self._object_type
        self.object_list = object_list
        self.delta_magnorm = delta_magnorm

    @property
    def native_columns(self):
        return ()

    def __getitem__(self, key):
        star_object = self.object_list[key]
        if not isinstance(star_object, StarObject):
            raise RuntimeError("expected StarObject")
        return BrighterStarsObject(star_object, self.delta_magnorm, self, key)

    def __len__(self):
        return self.object_list._total_len

    @staticmethod
    def register(sky_catalog, object_type):
        sky_catalog.cat_cxt.register_source_type(
            BrighterStarsCollection._object_type,
            object_class=BrighterStarsObject,
            collection_class=BrighterStarsCollection,
            custom_load=True
        )

    @staticmethod
    def load_collection(region, sky_catalog, mjd=None, **kwds):
        object_type = BrighterStarsCollection._object_type
        config = dict(sky_catalog.raw_config["object_types"][object_type])
        object_list = sky_catalog.get_object_type_by_region(region, "star")
        return BrighterStarsCollection(object_list, config['delta_magnorm'])
