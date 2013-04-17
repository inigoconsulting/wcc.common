from Products.CMFCore.utils import getToolByName
from zope.event import notify
from z3c.caching.purge import Purge

def purge_homepage(obj, event):
    catalog = getToolByName(obj, 'portal_catalog')
    for brain in catalog(portal_type='wcc.homepage.homepage'):
        notify(Purge(brain.getObject()))
