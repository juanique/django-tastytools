from tastypie.api import Api as TastyApi
from tastypie.resources import Resource as TastyResource, ModelResource as TastyModelResource
import json
import inspect


def _resources_from(module):
    for name in dir(module):
        o = getattr(module, name)
        try:
            if (o != TastyResource) and (o != TastyModelResource) and issubclass(o, TastyResource):
                yield o
        except TypeError: pass

class Api(TastyApi):
            
    def resource(self, resource_name):
        return self._registry[resource_name]
        
    def register(self, resource=None, canonical=True, **kwargs):
        resource_list = []

        if resource is not None:
            resource_list.append(resource)            
        if 'resources' in kwargs:
            resource_list += kwargs['resources']
        if 'modules' in kwargs:
            for module in kwargs['modules']:
                resource_list += _resources_from(module)

        for resource in resource_list:
            if inspect.isclass(resource):
                resource = resource()
            try:
                resource._meta.example = resource._meta.example_class(self)
            except AttributeError:
                pass
            super(Api, self).register(resource, canonical)        
        
    def get_resource_example_data(self, resource_name, method):
        return getattr(self.resource(resource_name)._meta.example,
            method.lower())

    def resource_allows_method(self, resource_name, method):
        options = self.resource(resource_name)._meta
        allowed = set(options.allowed_methods + options.detail_allowed_methods)
        return method.lower() in allowed

    def dehydrate(self, resource, obj, request=None):
        if type(resource) is str:
            resource = self.resource(resource)
        bundle = resource.build_bundle(obj=obj, request=request)
        bundle = resource.full_dehydrate(bundle)
        return json.loads(resource.serialize(None, bundle, 'application/json'))