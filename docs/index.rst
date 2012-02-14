Welcome to tastytools's documentation!
======================================

Contents:

.. toctree::
   :maxdepth: 2
   tutorial

Quick Start
===========

Assuming you have a tastypie api:

1. Add ``tastytools`` to ``INSTALLED_APPS``.
2. Create an ``api`` directory in your project root  with a bare ``__init__.py``.
3. Create an ``api/<my_app>.py`` file and place the following in it::

    from tastytools.api import Api
    from <my_app>.api.resources import MyModelResource, AnoterResource, YetAnotherResource

    api = Api()
    api.register(MyModelResource)
    api.register(resources=[AnotherResource, YetAnotherResource])

4. In your root URLconf, add the following code (around where the tastypie code might be)::

    from tastypie.api import Api
    from my_app.api.resources import MyModelResource

    api_name = 'v1'
    v1_api = Api(api_name=api_name)
    v1_api.register(MyModelResource())

    urlpatterns = patterns('',
      # ...more URLconf bits here...
      # Then add:
      (r'^tastytools/', include('tastytools.urls'), {'api_name': api_name}),
    )



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

