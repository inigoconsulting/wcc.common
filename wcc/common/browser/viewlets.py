from plone.app.layout.viewlets.common import LogoViewlet as BaseLogoViewlet
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class LogoViewlet(BaseLogoViewlet):

    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        super(LogoViewlet, self).update()

        lang = self.portal_state.language()
        portal = self.portal_state.portal()
        logoTitle = self.portal_state.portal_title()

        logoName = 'logo-%s.png' % lang
        if hasattr(portal, logoName):
            self.logo_tag = portal.restrictedTraverse(logoName
                    ).tag(title=logoTitle, alt=logoTitle)

        navroot = self.portal_state.navigation_root()
        if hasattr(navroot, 'getField'):
            self.navigation_root_description = navroot.getField(
                'description').get(navroot)
        else:
            self.navigation_root_description = u''
