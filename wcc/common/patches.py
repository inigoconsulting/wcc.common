import logging
logger = logging.getLogger('wcc.policy.patches')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARN)

def _patch_dont_compress_types():
    from ZPublisher.HTTPResponse import HTTPResponse
    NO_COMPRESSION_TYPES=['application/x-shockwave-flash']

    if getattr(HTTPResponse, '__inigo_dont_compress_types_patch', False):
        return 
    logger.info('Patching with exclude mimetype for compression patch')

    _orig_enableHTTPCompression = HTTPResponse.enableHTTPCompression
    def enableHTTPCompression(self, *args, **kwargs):
        if self.headers.get('content-type', '') in NO_COMPRESSION_TYPES:
            return 0
        return _orig_enableHTTPCompression(self, *args, **kwargs)

    HTTPResponse.enableHTTPCompression = enableHTTPCompression
    HTTPResponse.__inigo_dont_compress_types_patch = True

_patch_dont_compress_types()


def _patch_catalogcontentlisting_titleid():
    from plone.app.contentlisting.catalog import CatalogContentListingObject

    if getattr(CatalogContentListingObject,'pretty_title_or_id',False):
        return

    def pretty_title_or_id(self):
        return self._brain.pretty_title_or_id

    CatalogContentListingObject.pretty_title_or_id = pretty_title_or_id

_patch_catalogcontentlisting_titleid()



def _patch_collectiveinterface_reindex():
    from collective.interfaces.browser import InterfacesView

    if getattr(InterfacesView, '__inigo_collectiveinterfaces_reindex_patched',
            False):
        retrurn 

    _orig_call = InterfacesView.__call__
    def __call__(self):
        _orig_call(self)
        self.context.reindexObject(['object_provides'])

    InterfacesView.__call__ = __call__
    InterfacesView.__inigo_collectiveinterfaces_reindex_patched = True

_patch_collectiveinterface_reindex()


def _patch_collectivecontentleadimageblob_languageindependent():
    try:
        from collective.contentleadimage.extender import HAS_BLOB
        from collective.contentleadimage.extender import LeadImageBlobExtender
    except:
        return

    for f in LeadImageBlobExtender.fields:
        if f.__name__ == 'leadImage':
            f.languageIndependent = True

_patch_collectivecontentleadimageblob_languageindependent()


def _patch_multilingual_catalog_singlelang():
    from plone.app.multilingual import catalog

    if getattr(catalog, '__inigo_patched_singlelang', False):
        return

    _orig_language_filter = catalog.language_filter
    def language_filter(query):
        old_path = query.get('path', None)
        if isinstance(old_path, dict) and 'query' in old_path:
            if not old_path['query'] or (
                    isinstance(old_path['query'], list)):
                query['Language'] = 'all'
        return _orig_language_filter(query)

    catalog.language_filter = language_filter
    catalog.__inigo_patched_singlelang = True

_patch_multilingual_catalog_singlelang()


def _patch_galleria_default_height():
    try:
        from collective.ptg.galleria import IGalleriaDisplaySettings
    except ImportError:
        return

    IGalleriaDisplaySettings['galleria_height'].default = 600

_patch_galleria_default_height()


def _patch_improve_search_relevance():
    # this patch makes contents which search string exist in title as higher
    # relevance

    from plone.app.search.browser import Search
    from plone.app.contentlisting.interfaces import IContentListing
    from Products.CMFPlone.PloneBatch import Batch

    if getattr(Search, '__inigo_relevance_patched', False):
        return 

    _orig_results = Search.results
    def results(self, query=None, batch=True, b_size=10, b_start=0):
        results = _orig_results(self, query, batch, b_size, b_start)
        if not results:
            return results

        if query is None:
            query = {}

        query = self.filter_query(query)

        if not 'SearchableText' in query:
            return results

        if query.get('sort_on', ''):
            return results

        if batch:
            items = results._sequence._basesequence
        else:
            items = results._basesequence

        searchtext = query.get('SearchableText', '').lower().strip()
        searchterms = searchtext.split()
        def sortkey(x):
            title = x.Title.lower().strip()
            if title == searchtext:
                return 999
            if searchtext in title:
                return 900
            score = 0
            for term in searchterms:
                if term in title:
                    score += 1
            return score

        items = list(reversed(sorted(items, key=sortkey)))

        results = IContentListing(items)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    Search.results = results
    Search.__inigo_relevance_patched = True

_patch_improve_search_relevance()

# XXX only required for accessing manage_components
#
#def _patch_genericsetup_get_dotted_name():
#    from Products.GenericSetup import utils
#
#    if getattr(utils, '__inigo_patched', False):
#        return
#
#    _orig_getDottedName = utils._getDottedName
#    def _getDottedName(named):
#        if isinstance(named, basestring):
#            return str(named)
#
#        _marker = []
#        if getattr(named, '__name__', _marker) is _marker:
#            named.__name__ = ''
#
#        return _orig_getDottedName(named)
#
#    utils._getDottedName = _getDottedName
#    utils.__inigo_patched = True
#
#_patch_genericsetup_get_dotted_name()
