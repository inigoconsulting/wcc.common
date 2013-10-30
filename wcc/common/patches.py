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

def relevance_sortkey_factory(searchtext):
    searchterms = searchtext.split()
    def sortkey(x):
        title = x.Title.lower().strip()
        if title == searchtext:
            return 9999
        if searchtext in title:
            return 9000
        score = 0
        for term in searchterms:
            if term in title:
                score += len(term)
        return score
    return sortkey

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
        sortkey = relevance_sortkey_factory(searchtext)
        items = list(sorted(items, key=sortkey, reverse=True))

        results = IContentListing(items)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    Search.results = results
    Search.__inigo_relevance_patched = True

_patch_improve_search_relevance()

def _patch_improve_similar_items_relevance():
    # this patch makes 404 page list contents which url id exist in 
    # title as higher relevance

    from plone.app.redirector.browser import FourOhFourView
    from plone.app.redirector.interfaces import IRedirectionPolicy
    from zope.component import queryUtility, getMultiAdapter
    from Products.CMFCore.utils import getToolByName
    from Products.ZCTextIndex.ParseTree import QueryError, ParseError
    from Acquisition import aq_base, aq_inner

    if getattr(FourOhFourView,'__inigo_relevance_patched', False):
        return 

    def search_for_similar(self):
        path_elements = self._path_elements()
        if not path_elements:
            return None
        path_elements.reverse()

        policy = IRedirectionPolicy(self.context)

        ignore_ids = policy.ignore_ids

        portal_catalog = getToolByName(self.context, "portal_catalog")
        portal_state = getMultiAdapter((aq_inner(self.context), self.request),
             name='plone_portal_state')
        navroot = portal_state.navigation_root_path()
        for element in path_elements:
            # Prevent parens being interpreted
            element=element.replace('(', '"("')
            element=element.replace(')', '")"')
            # remove .html extensions
            element=element.replace('.html','')
            element=element.replace('.htm','')
            # wildcard the title search
            element=element.replace('-', '* *')
            element='*%s*' % element
            element = element.lower()
            if element not in ignore_ids:
                try:
                    result_set = portal_catalog(Title=element,
                        path = navroot,
                        portal_type=portal_state.friendly_types())
                    if result_set:
                        sortkey = relevance_sortkey_factory(element)
                        return list(sorted(result_set, key=sortkey, reverse=True))[:10]
                except (QueryError, ParseError):
                    # ignore if the element can't be parsed as a text query
                    pass

        for element in path_elements:
            # Prevent parens being interpreted
            element=element.replace('(', '"("')
            element=element.replace(')', '")"')
            # remove .html extensions
            element=element.replace('.html','')
            element=element.replace('.htm','')
            element=element.lower()
            if element not in ignore_ids:
                try:
                    result_set = portal_catalog(SearchableText=element,
                        path = navroot,
                        portal_type=portal_state.friendly_types())
                    if result_set:
                        sortkey = relevance_sortkey_factory(element)
                        return list(sorted(result_set, key=sortkey, reverse=True))[:10]
                except (QueryError, ParseError):
                    # ignore if the element can't be parsed as a text query
                    pass

        return []

    FourOhFourView.search_for_similar = search_for_similar
    FourOhFourView.__inigo_relevance_patched = True

_patch_improve_similar_items_relevance()


def _path_improve_autocomplete_search():

    from plone.app.vocabularies import catalog

    if getattr(catalog, '__inigo_patched', False):
        return

    _parse_query = catalog.parse_query
    def parse_query(query, path_prefix=''):
        q = _parse_query(query, path_prefix)
        if q.has_key('SearchableText'):
            q['Title'] = q['SearchableText']
            del q['SearchableText']
        return q

    catalog.parse_query = parse_query
    catalog.__inigo_patched = True

_path_improve_autocomplete_search()


def _patch_rtvideo_include_youtube_param():

    try:
        from collective.rtvideo.youtube.browser import videoembedcode
    except ImportError:
        return

    from urlparse import urlparse

    if getattr(videoembedcode, '__inigo_patched', False):
        return

    _orig_getVideoLink = videoembedcode.ClassicYoutubeEmbedCode.getVideoLink
    def getVideoLink(self):
        link = _orig_getVideoLink(self)
        qs = urlparse(self.context.getRemoteUrl())[4]
        if qs and qs.strip():
            params = qs.split('&')
            newparams = ''
            for param in params:
                k, v = param.split('=')
                if k not in ['v','list']:
                    newparams += '&' + param
            return '%s?%s' % (link, newparams)
        return link

    videoembedcode.ClassicYoutubeEmbedCode.getVideoLink = getVideoLink

    _orig_getEmbedVideoLink = videoembedcode.ShortYoutubeEmbedCode.getEmbedVideoLink
    def getEmbedVideoLink(self):
        link = _orig_getEmbedVideoLink(self)
        qs = urlparse(self.context.getRemoteUrl())[4]
        if qs and qs.strip():
            params = qs.split('&')
            newparams = ''
            for param in params:
                k, v = param.split('=')
                if k not in ['v', 'list']:
                    newparams += '&' + param
            return '%s?%s' % (link, newparams)
        return link

    videoembedcode.ShortYoutubeEmbedCode.getEmbedVideoLink = getEmbedVideoLink

    videoembedcode.__inigo_patched = True

_patch_rtvideo_include_youtube_param()

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
