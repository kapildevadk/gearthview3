# This is a generated file using Twisted's version.py module.
# It checks if the installed version of Twisted is compatible.

from twisted.version import version as twisted_version

minimum_compatible_version = (13, 0, 0)

if twisted_version < minimum_compatible_version:
    raise ImportError(f"Twisted version {minimum_compatible_version} or higher is required. "
                      f"Currently installed version is {twisted_version}.")
