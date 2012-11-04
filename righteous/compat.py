import six

urlencode = quote = None
if six.PY3:
    import urllib.parse
    urlencode = urllib.parse.urlencode
    quote = urllib.parse.quote
else:
    import urllib
    urlencode = urllib.urlencode
    quote = urllib.quote
