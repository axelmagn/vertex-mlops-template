import importlib
import logging


def dynamic_import_func(import_path: str):
    """Import a function dynamically by its path."""
    # TODO(axelmagn): input validation and graceful failure
    module_name, func_name = import_path.rsplit('.', 1)
    logging.debug(
        f"Importing function `{func_name}` from module `{module_name}`.")
    module = importlib.import_module(module_name)
    if module is None:
        raise ValueError(
            f"Could not import `{module_name}`: import returned None.")
    func = getattr(module, func_name)
    if func is None:
        raise ValueError(
            f"Could not get function `{func_name}` from module `{module_name}`: getattr returned None.")
    return func


def get_collection(collection, key, default={}):
    """Returns dict_in[key] or {}, interpreting None values in dict as unset.

    If key is a list, it is treated as a key traversal.

    This is useful for configs, where the configured value is often None, 
    but should be interpreted as an empty collection.
    """
    if isinstance(key, list):
        out = collection
        for k in key:
            out = get_collection(out, k)
    else:
        out = collection.get(key, None)
    return out if out is not None else default.copy()
