from zope.component.hooks import getSite
from email import message_from_string
from Products.CMFCore.utils import getToolByName

def notify_edit_by_nonmanager(obj, event):
    site = getSite()

    mtool = getToolByName(site, 'portal_membership')
    if not mtool.isAnonymousUser():
        user = mtool.getAuthenticatedMember()
        if user.has_role('Manager'):
            return

    state = site.restrictedTraverse('@@plone_portal_state')
    if obj.Language() and obj.Language() != state.language():
        return

    message = '''From: "%(email_from_name)s" <%(email_from_address)s>
To: "Web Editor" <webeditor@wcc-coe.org>
Subject: Content edited at %(url)s

%(url)s has been edited. Please review.
    '''

    encoding = site.getProperty('email_charset', 'utf-8')
    mail_text = message % {
        'url': obj.absolute_url(),
        'email_from_name': site.email_from_name,
        'email_from_address': site.email_from_address,
    }

    message_obj = message_from_string(mail_text)

    mTo = message_obj['To']
    mFrom = message_obj['From']
    subject = message_obj['Subject']

    site.MailHost.send(mail_text, mTo, mFrom, subject=subject,
                        charset=encoding)
