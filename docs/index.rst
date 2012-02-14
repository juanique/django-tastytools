Welcome to tastytools's documentation!
======================================

Tastytools is a set for usefull tools to develop a quality tastypie webservice
API.

It's main features are automatic documentation and the generation of Hygiene
tests (tests that ensure the pressence of certain features that that do not
give positive satisfaction, though dissatisfaction results from their absence).
For example it tests the pressence of help fields
An example in the case of an API, is a help text on the fields

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

5. got to http://localhost:8000/tastytools/v1/.

As you can see, now you have documentation for anyone who wants to consume
your api resources!

Requirements
============

Tastytools requires Tastypie to work. If you use Pip_, you can install
the necessary bits via the included ``requirements.txt``:

* django-tastypie (http://django-tastypie.readthedocs.org/)


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

