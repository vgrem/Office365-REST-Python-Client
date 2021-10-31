import sys

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

if is_py2:
    from urlparse import urlparse
    from urllib import quote
    from urlparse import urljoin
    import pytz as timezone
    from email import message_from_string as message_from_bytes_or_string
    from __builtin__ import xrange as range_or_xrange
elif is_py3:
    from urllib.parse import urlparse
    from urllib.parse import quote
    from urllib.parse import urljoin
    from datetime import timezone
    from email import message_from_bytes as message_from_bytes_or_string
    from builtins import range as range_or_xrange


def message_as_bytes_or_string(message):
    if is_py2:
        return message.as_string()
    else:
        return message.as_bytes()


def is_string_type(value):
    if is_py2:
        return isinstance(value, basestring)
    else:
        return type(value) is str


def is_absolute_url(url):
    return bool(urlparse(url).netloc)


def parse_query_string(url, key):
    if is_py2:
        import urlparse
        parsed_url = urlparse.urlparse(url)
        return urlparse.parse_qs(parsed_url.query)[key][0]
    else:
        from urllib.parse import urlparse
        from urllib.parse import parse_qs
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)[key][0]


def get_mime_type(file_name):
    if is_py2:
        from mimetypes import MimeTypes
        mime = MimeTypes()
        import urllib
        url = urllib.pathname2url(file_name)
        return mime.guess_type(url)
    else:
        import mimetypes
        return mimetypes.guess_type(file_name)
