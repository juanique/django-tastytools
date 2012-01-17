from tastypie.resources import ModelResource as TastyModelResource
from django.conf.urls.defaults import url
from tastypie import fields
from test.resources import TestData
from django.http import HttpResponse
from tastypie import http


class ModelResource(TastyModelResource):

    resource_uri = fields.CharField(help_text='URI of the resource.',
        readonly=True)

    def save_m2m(self, bundle):
        """
        Handles the saving of related M2M data.

        Due to the way Django works, the M2M data must be handled after the
        main instance, which is why this isn't a part of the main
        ``save`` bits.

        Currently slightly inefficient in that it will clear out the whole
        relation and recreate the related data as needed.
        """
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.readonly:
                continue

            # Get the manager.
            related_mngr = getattr(bundle.obj, field_object.attribute)

            if hasattr(related_mngr, 'clear'):
                # Clear it out, just to be safe.
                related_mngr.clear()

            related_objs = []

            for related_bundle in bundle.data[field_name]:
                related_bundle.obj.save()
                related_objs.append(related_bundle.obj)

            if not hasattr(related_mngr, 'add'):
                func = "save_m2m_%s" % field_name
                if not hasattr(self, func):
                    msg = "Missing save ManyToMany related %s function: %s."
                    msg %= (field_name, func)
                    raise Exception(msg)
                getattr(self, func)(bundle, related_objs)
            else:
                related_mngr.add(*related_objs)

    def override_urls(self):
        urlexp = r'^(?P<resource_name>%s)/example/'
        urlexp %= self._meta.resource_name
        return [url(urlexp, self.wrap_view('get_example_data_view'),
            name='api_get_example_data')
        ]

    def create_test_resource(self, force=False, *args, **kwargs):
        force = force or {}
        return self._meta.example.create_test_resource(force=force, *args,
            **kwargs)

    def create_test_model(self, data=None, *args, **kwargs):
        if data is None:
            data = {}

        return self._meta.example.create_test_model(data, *args, **kwargs)

    def get_test_post_data(self, data=None):
        if data is None:
            data = {}

        #print "getting post data from %s" % self._meta.example
        out = self._meta.example.post
        if isinstance(out, TestData):
            out = out.data

        return out

    def get_example_data_view(self, request, api_name=None,
        resource_name=None):

        if self._meta.example is not None:
            output = {
                    'POST': self._meta.example.post,
                    'GET': self._meta.example.get
            }

            requested_type = request.GET.get('type', 'False')
            try:
                output = output[requested_type.upper()]
            except KeyError:
                pass
            response_class = HttpResponse
        else:
            output = {
                    'error': 'missing api'
            }
            response_class = http.HttpBadRequest

        return self.create_response(request, output,
            response_class=response_class)
