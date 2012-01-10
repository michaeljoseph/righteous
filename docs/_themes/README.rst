righteous Sphinx Style
======================

This repository contains a sphinx style for righteous, derivde from  Kenneth Reitz's
request theme, which is turn a derivative of Mitsuhiko's themes for Flask and Flask related
projects.  To use this style in your Sphinx documentation, follow
this guide:

1. put this folder as _themes into your docs folder.  Alternatively
   you can also use git submodules to check out the contents there.

2. add this to your conf.py: ::

    sys.path.append(os.path.abspath('_themes'))
    html_theme_path = ['_themes']
    html_theme = 'righteous'

The following themes exist:

**righteous**
    based on the the small one-page flask_small theme.  Intended to be used by very small flask addon libraries.

