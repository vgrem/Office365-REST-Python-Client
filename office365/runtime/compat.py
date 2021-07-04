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
