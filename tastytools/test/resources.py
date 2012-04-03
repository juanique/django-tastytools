from django.db.models.fields.related import ManyRelatedObjectsDescriptor
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor
from django.db import IntegrityError, DatabaseError
from django.db.utils import ConnectionDoesNotExist
from django.core.management import call_command
from django.db import models

from tastytools.test import generators
import sys

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

    def set_related(self, obj):

        for args in self.related_data:
            args['force'] = {args['related_name']: obj}
            del args['related_name']
            self.set(**args)

    def set(self, name, constant=None, resource=None, count=None,
        force=False, related_name=False, id=None):

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
                        related=self.related, force=force, id=id)
                    value.append(res)
                    count -= 1
            else:
                value = self.create_test_data(resource,
                    related=self.related, force=force, id=id)
        else:
            value = constant

        self.data[name] = value

        return value

    def create_test_data(self, resource_name, related=Related.Model,
        force=False, id=None):
        force = force or {}

        resource = self.api.resource(resource_name)
        #resource.start_test_session(self.test_session)

        (uri, res) = resource.create_test_resource(force, id=id)

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

        return self.sample_data(related=Related.Uri).data

    @property
    def get(self):
        '''Returns sample GET data for the resource.'''

        (location, model) = self.create_test_resource()
        return self.api.dehydrate(resource=self.resource, obj=model)

    def create_test_resource(self, force={}, *args, **kwargs):
        '''Creates a test resource and obtains it's URI
        and related object'''

        model = self.create_test_model(force=force, *args, **kwargs)
        bundle = self.resource.build_bundle(obj=model)
        location = self.resource.get_resource_uri(bundle)
        return location, bundle.obj

    def save_test_obj(self, model):
        if self.db is not None:
            databases = [self.db]
        else:
            databases = ['tastytools', 'test', '']

        for db in databases:
            try:
                model.save(using=db)
            except ConnectionDoesNotExist:
                continue

        if model.pk is None:
            raise ConnectionDoesNotExist("Tried: %s" % ', '.join(databases))

    def create_test_model(self, data=False, force=False, id=None, *args,
            **kwargs):
        '''Creates a test model (or object asociated with the resource and
        returns it

        '''
        force = force or {}

        model_class = self.resource._meta.object_class

        data = data or self.sample_data(related=Related.Model, force=force,
                id=id)

        valid_data = {}
        m2m = {}
        class_fields = model_class._meta.get_all_field_names()
        for field in class_fields:
            try:
                valid_data[field] = data[field]

                try:
                    field_obj = model_class._meta.get_field(field)
                    is_m2m = isinstance(field_obj, ManyToManyField)
                except Exception:
                    field_obj = getattr(model_class, field)
                    is_m2m = isinstance(field_obj,
                        ForeignRelatedObjectsDescriptor)
                    is_m2m = is_m2m or isinstance(
                            field_obj, ManyRelatedObjectsDescriptor)

                if is_m2m:
                    m2m[field] = data[field]
                    del valid_data[field]

            except KeyError:
                pass

        model = model_class(**valid_data)

        try:
            # if we are running tests, use the default database
            if 'test' in sys.argv:
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
                        call_command('syncdb', database=db, interactive=False)
                        model.save(using=db)
                    except ConnectionDoesNotExist:
                        continue
        except IntegrityError as e:
            if id is not None:
                model = model_class.objects.get(**valid_data)
                #print "Got %s %s" % (model_class.__name__, id)
            else:
                raise e

        #print model

        for m2m_field, values in m2m.items():
            if type(values) is not list:
                values = [values]
            for value in values:
                getattr(model, m2m_field).add(value)

        data.set_related(model)
        return model

    #@property
    def sample_data(self, related=Related.Model, force=False, id=None):
        '''Returns the full a full set of data as an _meta.testdata for
        interacting with the resource

        '''
        model_class = self.resource._meta.object_class

        resource_fields = self.resource.fields

        data = TestData(self.api, force, related, id=id)

        fields = model_class._meta.fields
        for field in fields:
            if field.name in self.resource._meta.excludes:
                continue
            if isinstance(field, ForeignKey):
                if field.name in resource_fields:
                    resource_field = resource_fields[field.name]
                    data.set(field.name,
                            resource=resource_field.to._meta.resource_name)
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

        return self.get_data(data)

    def get_data(self, data):
        return data
