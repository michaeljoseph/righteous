urlencode = quote = None
try:
    import urllib.parse
    urlencode = urllib.parse.urlencode
    quote = urllib.parse.quote
except ImportError:
    import urllib
    urlencode = urllib.urlencode
    quote = urllib.quote
