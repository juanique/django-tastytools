from tastypie.api import Api as TastyApi
import json

class Api(object):

    def __init__(self, resources, api_name):

        self.tastypieApi = TastyApi(api_name)
        self.dummy_resources = []
        self.resources = {}

        for resource in resources:
            self.resources[resource._meta.resource_name] = resource
            self.tastypieApi.register(resource)
            try:
                resource._meta.example = resource._meta.example_class(self)
            except AttributeError:
                pass

    @property
    def urls(self):
        return self.tastypieApi.urls

    def get_resource_list_uri(self, resource_name):
        return self.resources[resource_name].get_resource_list_uri()

    def get_resource_example_data(self, resource_name, method):
        return getattr(self.resources[resource_name]._meta.example,
            method.lower())

    def resource_allows_method(self, resource_name, method):
        options = self.resources[resource_name]._meta
        allowed = set(options.allowed_methods + options.detail_allowed_methods)
        return method.lower() in allowed

    def dehydrate(self, resource, obj, request=None):
        if type(resource) is str:
            resource = self.resources[resource]
        bundle = resource.build_bundle(obj=obj, request=request)
        bundle = resource.full_dehydrate(bundle)
        return json.loads(resource.serialize(None, bundle, 'application/json'))

