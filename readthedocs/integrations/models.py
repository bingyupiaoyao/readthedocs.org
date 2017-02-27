"""Integration with external services"""

import json

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField


class HttpTransactionManager(models.Manager):

    """HTTP manager methods"""

    def from_transaction(self, req, resp, source=None, related_object=None):
        """Create object from Django request and response objects"""
        fields = {
            'status_code': resp.status_code,
            # This is the rawest form of request header we have, the WSGI
            # headers. HTTP headers are prefixed with `HTTP_`, which we remove,
            # and because the keys are all uppercase, we'll normalize them to
            # title case-y hyphen separated values.
            'request_headers': dict(
                (key[5:].title().replace('_', '-'), str(val))
                for (key, val) in req.META.items()
                if key.startswith('HTTP_')
            ),
            'request_body': req.data if hasattr(req, 'data') else req.body,
            'response_headers': dict(resp.items()),
            'response_body': req.data if hasattr(req, 'data') else resp.content,
        }
        if source is not None:
            fields['source'] = source
        if related_object is not None:
            fields['related_object'] = related_object
        return self.create(**fields)


class HttpTransaction(models.Model):

    """Record an HTTP transaction"""

    SOURCE_WEBHOOK = 'webhook'

    source = models.CharField(_('Source'), max_length=64)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')

    date = models.DateTimeField(_('Date'), auto_now_add=True)

    request_headers = JSONField(_('Request headers'), )
    request_body = models.TextField(_('Request body'))

    response_headers = JSONField(_('Request headers'), )
    response_body = models.TextField(_('Response body'))

    status_code = models.IntegerField(_('Status code'))

    objects = HttpTransactionManager()
