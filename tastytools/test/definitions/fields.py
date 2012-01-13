from django.test import TestCase
from klooff.test import MultiTestCase, create_multi_meta
from tastytools.test.client import Client
from datetime import datetime


def generate(api):
    class UnderResourceFields(MultiTestCase):

        @staticmethod
        def generate_field_test_data(field):
            field_classname = field.__class__.__name__
            if field_classname == 'CharField':
                bad_value = "abcd"
            elif field_classname == "IntegerField":
                bad_value = 12345
            elif field_classname == "ToManyField":
                (uri, res) = field.to_class().create_test_resource()
                return [uri]
            elif field_classname == "DateField":
                return datetime.now()
            else:
                raise Exception("Unrecognized classname: %s" % field_classname)

            return bad_value

        @staticmethod
        def multi_help(self, resource_name, resource, field_name, field):
            if field.help_text == field.__class__.help_text:
                msg = "Missing help text for %s.%s resource field."
                msg %= (resource_name, field_name)
                self.assertTrue(False, msg)

        @staticmethod
        def multi_readonly_post(self, resource_name, resource, field_name, field):
            client = Client()

            if field.readonly and resource.can_create():
                post_data = resource.get_test_post_data()

                bad_value = UnderResourceFields.generate_field_test_data(field)
                post_data[field_name] = bad_value

                post_response = client.post(resource.get_resource_list_uri(),
                    post_data, parse='json')

                if post_response.status_code == 201:
                    location = post_response['Location']
                    get_response = client.get(location, parse='json')

                    msg = "%s.%s can be set by a POST request even though it's readonly!."
                    msg %= (resource_name, field_name)

                    self.assertNotEqual(get_response.get(field_name, ''),
                       bad_value, msg)

        @staticmethod
        def multi_readonly_patch(self, resource_name, resource, field_name, field):
            client = Client()

            if field.readonly and resource.can_create():
                #Create a resource to modify it
                (location, obj) = resource.create_test_resource()
                bad_value = UnderResourceFields.generate_field_test_data(field)

                #authenticate to be allowed to modify the resource
                post_data = api.resources['userprofile'].get_test_post_data()
                client.login(username=post_data['email'],
                    password=post_data['password'])

                #attempt to PATCH
                patch_data = {}
                patch_data[field_name] = bad_value
                patch_response = client.patch(location, patch_data, parse='json')
                get_response = client.get(location, parse='json')

                msg = "%s.%s can be changed by a PATCH and it's readonly!."
                msg %= (resource_name, field_name)

                self.assertNotEqual(get_response.data.get(field_name, None),
                    bad_value, msg)

        @staticmethod
        def generate_arguments():
            args = []
            for resource_name, resource in api.resources.items():
                for field_name, field in resource.fields.items():
                    args.append((resource_name, resource, field_name, field))

            return args

        @staticmethod
        def generate_test_name(resource_name, resource, field_name, field):
            return "_".join([resource_name, field_name])


    class TestResourceFields(TestCase):
        __metaclass__ = create_multi_meta(UnderResourceFields)

    return TestResourceFields
