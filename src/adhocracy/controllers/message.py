import logging

from formencode import htmlfill, Invalid, Schema, validators

from pylons import request, tmpl_context as c
from pylons.controllers.util import redirect
from pylons.i18n import _

from adhocracy import model
from adhocracy.lib import helpers as h
from adhocracy.lib import message as _message
from adhocracy.lib.auth import require
from adhocracy.lib.base import BaseController
from adhocracy.lib.templating import render
from adhocracy.lib.util import get_entity_or_abort
from adhocracy.lib.message import send as send_message

log = logging.getLogger(__name__)


class MessageCreateForm(Schema):
    allow_extra_fields = True
    subject = validators.String(max=250, not_empty=True)
    body = validators.String(max=20000, min=2, not_empty=True)


class MessageController(BaseController):

    def new(self, id, format='html', errors={}):
        c.page_user = get_entity_or_abort(model.User, id)
        require.user.message(c.page_user)
        html = render("/message/new.html", overlay=format == u'overlay')
        return htmlfill.render(html, defaults=request.params,
                               errors=errors, force_defaults=False)

    def create(self, id, format='html'):
        c.page_user = get_entity_or_abort(model.User, id)
        require.user.message(c.page_user)
        try:
            self.form_result = MessageCreateForm().to_python(request.params)
        except Invalid, i:
            return self.new(id, errors=i.unpack_errors())

        body = self.form_result.get('body')
        subject = self.form_result.get('subject')

        send_message(subject, body, c.user, [c.page_user], instance=c.instance,
                     massmessage=False)

        h.flash(_("Your message has been sent. Thanks."), 'success')
        redirect(h.entity_url(c.page_user, instance=c.instance))

    def show(self, id, format='html'):
        c.message = get_entity_or_abort(model.Message, id)
        require.message.show(c.message)
        c.body = _message.render_body(c.message.body, c.user)
        return render('/message/show.html', overlay=format == 'overlay')
