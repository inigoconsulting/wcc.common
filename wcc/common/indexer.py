from plone.app.dexterity.behaviors.metadata import ICategorization
from collective.dexteritytextindexer.utils import searchable

searchable(ICategorization, 'subjects')
