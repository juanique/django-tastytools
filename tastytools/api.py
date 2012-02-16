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
    
    _testdata_classes = {}
            
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
            self._bind_testdata(resource._meta.resource_name)
    
    def register_testdata(self, testdata_class):
        self._testdata_classes[testdata_class.resource] = testdata_class
        self._bind_testdata(testdata_class.resource)

    def _bind_testdata(self, resource_name):
        testdata_class = self._testdata_classes.get(resource_name)
        resource = self._registry.get(resource_name)
        
        if testdata_class is None:
            return
        if resource_name is None:
            return
            
        resource._meta.testdata_class = testdata_class
        resource._meta.testdata = testdata_class(self)
        
    def get_resource_example_data(self, resource_name, method):
        return getattr(self.resource(resource_name)._meta.testdata,
            method.lower())

    def resource_allows_method(self, resource_name, method):
        options = self.resource(resource_name)._meta
        allowed = set(options.allowed_methods + options.detail_allowed_methods)
        return method.lower() in allowed
    
    def resource_allows_detail(self, resource_name, method):
        options = self.resource(resource_name)._meta
        return method.lower() in options.detail_allowed_methods
        

    def dehydrate(self, resource, obj, request=None):
        if type(resource) is str:
            resource = self.resource(resource)
        bundle = resource.build_bundle(obj=obj, request=request)
        bundle = resource.full_dehydrate(bundle)
        return json.loads(resource.serialize(None, bundle, 'application/json'))
