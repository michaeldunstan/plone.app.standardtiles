# -*- coding: utf-8 -*-

from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema

from plone.app.standardtiles import _PMF as _
from plone.namedfile.field import NamedBlobFile
from plone.supermodel.model import Schema
from plone.tiles import PersistentTile
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

try:
    from plone.protect.interfaces import IDisableCSRFProtection
    HAS_PLONE_PROTECT = True
except ImportError:
    HAS_PLONE_PROTECT = False


def get_settings():
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IImagingSchema,
                                     prefix="plone",
                                     check=False)
    return settings


@provider(IContextSourceBinder)
def image_scales(context):
    values = []
    settings = get_settings()
    for allowed_size in settings.allowed_sizes:
        name = allowed_size.split()[0]
        if name not in ("thumb", "tile", "icon", "listing"):
            values.append(SimpleTerm(name, name, _(allowed_size)))
    return SimpleVocabulary(values)


class IImageTile(Schema):

    image = NamedBlobFile(
        title=_(u'Please, upload an image'),
    )

    scale = schema.Choice(
        title=_(u'Select maximum display size'),
        source=image_scales
    )


class ImageTile(PersistentTile):
    """Image tile.

    This is a persistent tile which stores an image with
    selected image scale.

    When rendered, the tile will output an <img /> tag like::

    <img src=".../@@plone.app.standardtiles.image/tile-id/
              @@images/bcc7be5d-75cc-4cfd-9d3a-4ad231aa01de.png" />

    """

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        # Disable CSRF, because imagescales may save a new scale into ZODB
        if HAS_PLONE_PROTECT:
            alsoProvides(self.request, IDisableCSRFProtection)
