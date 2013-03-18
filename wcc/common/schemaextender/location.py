from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.public import (LinesField, InAndOutWidget)
from five import grok
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from plone.app.collection.interfaces import ICollection
from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import RichWidget
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.interfaces.news import IATNewsItem
from Products.ATContentTypes.interfaces.event import IATEvent

from wcc.common import MessageFactory as _
from wcc.common.interfaces import IProductSpecific

class ExtensionLinesField(ExtensionField, LinesField):
    pass


class LocationTagsExtender(grok.Adapter):
    grok.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    grok.provides(IOrderableSchemaExtender)
    grok.baseclass()

    fields = [
        ExtensionLinesField('countries',
            vocabulary_factory='wcc.vocabulary.country',
            storage=AttributeStorage(),
            widget=InAndOutWidget(title=_(u'Related Countries'))
        ),
    ]

    layer = IProductSpecific

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, schematas):
        # you may reorder the fields in the schemata here
        return schematas



class NewsLocationTagsExtender(LocationTagsExtender):
    grok.context(IATNewsItem)

class EventLocationTagsExtender(LocationTagsExtender):
    grok.context(IATEvent)
