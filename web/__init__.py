from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cdt-disaster-recovery")
except PackageNotFoundError:
    # package is not installed
    pass
