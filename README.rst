=================
django-tastytools
=================

Useful tools for developing REST services with django-tastypie

*NOTE*: This repository is not being actively maintained, I'm doing a new version of this and I'm splitting the code into 3 parts:

https://github.com/juanique/django-chocolate - Which handles mockup models creation for unit testing
https://github.com/juanique/django-tastydocs - Which handles automatic web tastypie api documentation (it depends on django-chocolate)

And I still need to define a 3rd part which will cover automatic test generation for fuzzy testing and code quality.

The new code base is still new and lacks a lot of documentation. But is still recommended.

Requirements
============

Required
--------

* django-tastypie (http://django-tastypie.readthedocs.org/)


What iss It Look Like?
======================

Asuming you have a tastypie implemented api, a basic example looks like::

    # myapp/api/tools.py
    # ============
    from tastytools.api import Api
    from resources import MyModelResource, AnotherResource, YetAnotherResource

    api = Api()
    api.register(MyModelResource)
    api.register(resources=[AnotherResource, YetAnotherResource])


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

That gets you a basic automatic documentation for your api at /tastytools/doc/

You can find more in the documentation at
http://tastytools.readthedocs.org/.


What is tastytools?
===================
Useful tools for developing REST services with django-tastypie
