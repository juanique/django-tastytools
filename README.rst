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
    from resources import CommentResource, AnotherResource, YetAnotherResource

    api = Api()
    api.register(CommentResource)
    api.register(resources=[AnotherResource, YetAnotherResource])


    # api/tests.py
    # =======
    from tastytools.test.definitions import resources, fields
    from api.myapp import api

    ResourceTests = resources.generate(api)
    ResourceFieldTests = fields.generate(api)

That gets you a fully automatic documentation and auto-generated tests
for your api.

You can find more in the documentation at
http://django-tastytools.readthedocs.org/.


What is tastytools?
===================
Useful tools for developing REST services with django-tastypie

:author: Ignacio Munizaga
:date: 2011/09/16
