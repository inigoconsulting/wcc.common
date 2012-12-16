from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from plone.directives import form
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider

from plone.namedfile import field as namedfile
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from collective.miscbehaviors.behavior.utils import context_property

from wcc.churches import MessageFactory as _

class ILocationTags(form.Schema):

    countries = schema.List(
        title=_(u"Related Countries"),
        value_type = schema.Choice(
            vocabulary="wcc.vocabulary.country"
        ),
        required=False
    )

alsoProvides(ILocationTags,IFormFieldProvider)


class LocationTags(object):
    """
       Adapter for Location Tags
    """
    implements(ILocationTags)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    regions = context_property('regions')
    countries = context_property('countries')    
