from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pyds4")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
