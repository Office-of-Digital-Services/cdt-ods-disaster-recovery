from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ddrc-web")
except PackageNotFoundError:
    # package is not installed
    pass
