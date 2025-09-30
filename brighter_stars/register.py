from .stars import BrighterStarsCollection


__all__ = ['register_objects']


COLLECTION_CLASS_MAP = {"BrighterStarsCollection": BrighterStarsCollection}


def register_objects(sky_catalog, object_type):
    config = dict(sky_catalog.raw_config["object_types"][object_type])
    if "collection_class" not in config:
        return
    collection_class = COLLECTION_CLASS_MAP[config["collection_class"]]
    collection_class.register(sky_catalog, object_type)
