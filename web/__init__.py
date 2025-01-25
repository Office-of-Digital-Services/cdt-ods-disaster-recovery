from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ca-disaster-recovery")
except PackageNotFoundError:
    # package is not installed
    pass
