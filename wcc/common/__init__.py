# This package may contain traces of nuts
from wcc.common import patches

from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
MessageFactory = MessageFactory('wcc.common')

