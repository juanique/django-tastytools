from django.db.models.fields.related import ManyRelatedObjectsDescriptor
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor
from django.db.utils import ConnectionDoesNotExist
from django.db import  DatabaseError
from django.core.management import call_command
from django.db import models
from tastytools.test import generators

FIELDCLASS_TO_GENERATOR = {
    models.BooleanField: generators.BooleanGenerator,
    models.DateField: generators.DateGenerator,
    models.DateTimeField: generators.DateTimeGenerator,
    models.EmailField: generators.EmailGenerator,
    models.IntegerField: generators.IntegerGenerator,
    models.FloatField: generators.FloatGenerator,
    models.IPAddressField: generators.IPAddressGenerator,
    models.NullBooleanField: generators.NullBooleanGenerator,
    models.PositiveIntegerField: generators.PositiveIntegerGenerator,
    models.PositiveSmallIntegerField: generators.PositiveSmallIntegerGenerator,
    models.SlugField: generators.SlugGenerator,
    models.SmallIntegerField: generators.SmallIntegerGenerator,
    models.TextField: generators.LoremGenerator,
    models.TimeField: generators.TimeGenerator,
    models.URLField: generators.URLGenerator,
    # field generators
    models.CharField: generators.CharFieldGenerator,
    models.DecimalField: generators.DecimalFieldGenerator,
    models.FilePathField: generators.FilePathFieldGenerator,
}


class Related(object):
    '''Constants holder class for various types of data generation modes'''

    Model = "MODEL"
    Uri = "URI"
    Full = "FULL"


class TestData(object):

    def __init__(self, api, force=None, related=None, id=None):
        self.api = api
        self.force = force or {}
        self.related = related
        self.data = {}
        self.related_data = []
        self.id = id

    def __getitem__(self, name):
        return self.data[name]

    def __setitem__(self, name, value):
        self.data[name] = value

    def __delitem__(self, name):
        del self.data[name]

    def update(self, data):
        return self.data.update(data)

    def to_dict(self):
        return self.data

    def set_related(self, obj, example=False):

        for args in self.related_data:
            args['force'] = {args['related_name']: obj}

            del args['related_name']
            self.set(example=example, **args)

    def set(self, name, constant=None, resource=None, count=None,
        force=False, related_name=False, id=None, example=False):

        if related_name:
            self.related_data.append({
                'name': name,
                'constant': constant,
                'resource': resource,
                'count': count,
                'related_name': related_name,
            })
            return

        value = None
        force = force or {}

        if name in self.force:
            value = self.force[name]
        elif resource is not None:
            if count > 0:
                value = []
                while count > 0:
                    res = self.create_test_data(resource,
                        related=self.related, force=force, id=id,
                        model=constant, example=example)
                    value.append(res)
                    count -= 1
            else:
                value = self.create_test_data(resource, example=example,
                    related=self.related, force=force, id=id, model=constant)
        #elif constant is not None:
        else:
            value = constant

        self.data[name] = value

        return value

    def create_test_data(self, resource_name, related=Related.Model,
        force=False, id=None, model=None, example=False):
        force = force or {}

        resource = self.api.resource(resource_name)
        #resource.start_test_session(self.test_session)

        if model is not None:
            uri = resource.get_resource_uri(model)
            res = model
        else:
            (uri, res) = resource.create_test_resource(force, id=id, example=example)

        if related == Related.Uri:
            return uri
        elif related == Related.Model:
            return res
        elif related == Related.Full:
            return self.api.dehydrate(resource=resource_name, obj=res)

        raise Exception("Missing desired related type. Given: %s" % related)


class ResourceTestData(object):

    test_session = None

    def __init__(self, api, resource=None, db=None):
        '''Constructor - requires the resource name or class to be registered
        on the given api.'''

        if resource is None:
            resource = self.resource

        if resource is None:
            msg = "ResourceTestData initialized without a resource. "\
                "Did you forget to override the constructor?"
            raise Exception(msg)

        self.api = api
        if type(resource) is str:
            resource = self.api.resource(resource)
        self.resource = resource

        self.db = db

    @property
    def post(self):
        '''Returns sample POST data for the resource.'''

        return self._post()

    def _post(self, example=False):
        '''Returns sample POST data for the resource.'''

        return self.sample_data(related=Related.Uri, example=example).data

    @property
    def get(self):
        """Returns sample GET data for the resource."""
        return self._get()

    def _get(self, example=False):
        """Returns sample GET data for the resource."""
        (location, model) = self.create_test_resource(example=example)
        return self.api.dehydrate(resource=self.resource, obj=model)


    def create_test_resource(self, force={}, example=False, *args, **kwargs):
        '''Creates a test resource and obtains it's URI
        and related object'''

        model = self.create_test_model(force=force, example=example, *args, **kwargs)
        bundle = self.resource.build_bundle(obj=model)
        location = self.resource.get_resource_uri(bundle)
        return location, bundle.obj

    def save_test_obj(self, model, example=False):
        """ sabes the test object to database.

        If this is an example (for the docs page):
            save it to the tastytools specified database, or, one of the
            fallbachs ('the only fallback now is tastytools')
        else:
            save it to the default database

        """
        if not example:
            databases = ['']
        elif self.db is not None:
            databases = [self.db]
        else:
            databases = ['tastytools', '']

        for db in databases:
            try:
                model.save(using=db)
            except ConnectionDoesNotExist:
                continue
            except DatabaseError:
                try:
                    call_command('syncdb', migrate=True, database=db, interactive=False)
                    model.save(using=db)
                except ConnectionDoesNotExist:
                    continue

        if model.pk is None:
            model.save()

    def get_model_cache(self):
        if not hasattr(self.resource, "_models"):
            self.resource._models = {}
        return self.resource._models

    def get_cached_model(self, id):
        return self.get_model_cache().get(id, None)

    def set_cached_model(self, id, model):
        if id is not None:
            self.get_model_cache()[id] = model

    def create_test_model(self, data=False, force=False, id=None,
            example=False, *args, **kwargs):
        '''Creates a test model (or object asociated with the resource and
        returns it

        '''
        cached_model = self.get_cached_model(id)
        if cached_model is not None:
            cached_model.save()
            return cached_model

        force = force or {}

        model_class = self.resource._meta.object_class

        data = data or self.sample_data(related=Related.Model, force=force,
                id=id, example=example)

        valid_data = {}
        m2m = {}
        class_fields = model_class._meta.get_all_field_names()
        for field in class_fields:
            try:
                value = data[field]
            except KeyError:
                continue

            valid_data[field] = value

            try:
                field_obj = model_class._meta.get_field(field)
                is_m2m = isinstance(field_obj, ManyToManyField)
            except Exception:
                field_obj = getattr(model_class, field)
                is_m2m = isinstance(field_obj,
                    ForeignRelatedObjectsDescriptor)
                is_m2m = is_m2m or isinstance(field_obj, ManyRelatedObjectsDescriptor)

            if is_m2m:
                m2m[field] = data[field]
                del valid_data[field]


        model = model_class(**valid_data)

        self.save_test_obj(model, example=example)

        for m2m_field, values in m2m.items():
            if type(values) is not list:
                values = [values]
            for value in values:
                getattr(model, m2m_field).add(value)
        data.set_related(model, example=example)
        self.set_cached_model(id, model)
        return model

    #@property
    def sample_data(self, related=Related.Model, force=False, id=None, example=False):
        '''Returns the full a full set of data as an _meta.testdata for
        interacting with the resource

        '''
        model_class = self.resource._meta.object_class

        resource_fields = self.resource.fields

        data = TestData(self.api, force, related)

        data = self.get_data(data)

        fields = model_class._meta.fields
        for field in fields:
            if field.name in self.resource._meta.excludes:
                continue
            if field.name in data.data:
                continue
            if isinstance(field, ForeignKey):
                if field.name in resource_fields:
                    resource_field = resource_fields[field.name]
                    data.set(field.name,
                        resource=resource_field.to_class()._meta.resource_name,
                        example=example)
            else:
                if type(field) in FIELDCLASS_TO_GENERATOR:
                    generator_class = FIELDCLASS_TO_GENERATOR[type(field)]
                    if issubclass(generator_class, generators.FieldGenerator):
                        generator = generator_class(field)
                    elif issubclass(generator_class, generators.Generator):
                        generator = generator_class()
                    value = generator.get_value()
                    if value is not None:
                        data.set(field.name, value)
        return data

    def get_data(self, data):
        return data
