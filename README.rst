===============
django-tastytools
===============

Useful tools for developing REST services with django-tastypie

Requirements
============

Required
--------

* django-tastypie (http://django-tastypie.readthedocs.org/)


What iss It Look Like?
======================

Asuming you have a tastypie implemented api, a basic example looks like::

    # api/myapp.py
    # ============
    from tastytools.api import Api
    from resources import MyModelResource, AnotherResource, YetAnotherResource

    api = Api()
    api.register(MyModelResource)
    api.register(resources=[AnotherResource, YetAnotherResource])


    # api/tests.py
    # =======
    from tastytools.test.definitions import resources, fields
    from api.myapp import api

    ResourceTests = resources.generate(api)
    ResourceFieldTests = fields.generate(api)

    # urls.py
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

That gets you a fully automatic documentation and auto-generated tests
for your api.

You can find more in the documentation at
http://django-tastytools.readthedocs.org/.


What is tastytools?
===================
Useful tools for developing REST services with django-tastypie

:author: Ignacio Munizaga
:date: 2011/09/16
