from tastypie.api import Api as TastyApi
from tastypie.resources import Resource as TastyResource, ModelResource as TastyModelResource
from tastytools.resources import ModelResource as ToolsResource
import json
import inspect


def _resources_from(module):
    for name in dir(module):
        o = getattr(module, name)
        try:
            base_classes = [ToolsResource, TastyResource, TastyModelResource]
            is_base_class = o in base_classes
            is_resource_class =  issubclass(o, TastyResource)

            if is_resource_class and not is_base_class:
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
            
            super(Api, self).register(resource, canonical)        

            try:
                resource._meta.example = resource._meta.example_class(self)
            except AttributeError as e:
                msg = "%s: Did you forget to define the example class for %s?"
                msg %= (e, resource.__class__.__name__)
                raise Exception(msg)
        
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
