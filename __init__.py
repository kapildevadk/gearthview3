# -*- coding: utf-8 -*-
"""
GEarth View - A QGIS plugin

This script initializes the plugin, making it known to QGIS.
"""

import sys
import os
import site

# Add the path to the extension libraries
site.addsitedir(os.path.abspath(os.path.dirname(__file__) + '/ext-libs'))

def name():
    """
    Return the plugin name
    """
    return "GEarthView"

def description():
    """
    Return the plugin description
    """
    return "GEarth View - A plugin to display 3D globe views in QGIS"

def version():
    """
    Return the plugin version
    """
    return "Version 1.0.5"

def icon():
    """
    Return the path to the plugin icon
    """
    return ":/plugins/gearthview/icon.png"

def qgisMinimumVersion():
    """
    Return the minimum QGIS version required to run this plugin
    """
    return "2.0"

def author():
    """
    Return the plugin author
    """
    return "geodrinx"

def email():
    """
    Return the plugin author email
    """
    return "geodrinx@gmail.com"

def classFactory(iface):
    """
    Load the gearthview class from the gearthview module
    """
    from .gearthview import gearthview
    return gearthview(iface)
