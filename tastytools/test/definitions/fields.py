from django.test import TestCase
from tastytools.test.client import Client, MultiTestCase, create_multi_meta
from datetime import datetime
from helpers import prepare_test_post_data


def generate(api, setUp=None):
    if setUp is None:
        def user_setUp(*args, **kwargs):
            return
    else:
        user_setUp = setUp
                
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
            elif field_classname == "ToOneField":
                (uri, res) = field.to_class().create_test_resource()
                return [uri]
            elif field_classname == "DateField":
                return datetime.now()
            else:
                raise Exception("Unrecognized classname: %s" % field_classname)

            return bad_value

        @staticmethod
        def multi_nice_messages(self, resource_name, resource, field_name, field):
            if resource.can_create():
                post_data = prepare_test_post_data(self, resource)
                try:
                    del post_data[field_name]
                except:
                    return

                response = self.client.post(resource.get_resource_list_uri(),
                    post_data)

                for code in [404, 500]:
                    msg = "%s returns a %s response when issuing a POST with missing %s"
                    msg %= (resource_name, code, field_name)
                    self.assertNotEqual(code, response.status_code, msg)
                header, content_type = response._headers['content-type']

                if len(response.content) > 0:
                    msg = "Bad content type when POSTing a %s with missing %s: %s (%s)=> %s"
                    msg %= (resource_name, field_name, content_type, response.status_code, response.content)
                    self.assertTrue(content_type.startswith('application/json'), msg)

        @staticmethod
        def multi_help(self, resource_name, resource, field_name, field):
            if field_name == 'id':
                return
            if field.help_text == field.__class__.help_text:
                msg = "Missing help text for %s.%s resource field."
                msg %= (resource_name, field_name)
                self.assertTrue(False, msg)

        @staticmethod
        def multi_readonly_post(self, resource_name, resource, field_name,
            field):

            if field.readonly and resource.can_create():
                post_data = resource.get_test_post_data()
                bad_value = UnderResourceFields.generate_field_test_data(field)
                post_data[field_name] = bad_value
                post_response = self.client.post(resource.get_resource_list_uri(),
                    post_data, parse='json')

                if post_response.status_code == 201:
                    location = post_response['Location']
                    get_response = self.client.get(location, parse='json')
                    msg ="Could not read posted resource (%d)\n%s"
                    msg %= (get_response.status_code, get_response.content)
                    self.assertEqual(get_response.status_code, 200, msg)

                    msg = "%s.%s can be set by a POST request even though"\
                        " it's readonly!."
                    msg %= (resource_name, field_name)
                    self.assertNotEqual(get_response.get(field_name, ''),
                       bad_value, msg)

        @staticmethod
        def multi_readonly_patch(self, resource_name, resource, field_name,
            field):

            client = Client()

            if field.readonly and resource.can_patch():
                #Create a resource to modify it
                (location, obj) = resource.create_test_resource()
                bad_value = UnderResourceFields.generate_field_test_data(field)

                #attempt to PATCH
                patch_data = {}
                patch_data[field_name] = bad_value
                self.client.patch(location, patch_data, parse='json')
                get_response = client.get(location, parse='json')

                msg = "%s.%s can be changed by a PATCH and it's readonly!\n%s"
                msg %= (resource_name, field_name, get_response)
                
                self.assertTrue(get_response.data is not None, "No response data from %s \nWith data: %s" % (location, patch_data))

                self.assertNotEqual(get_response.data.get(field_name, None),
                    bad_value, msg)

        @staticmethod
        def generate_arguments():
            args = []
            for resource_name, resource in api._registry.items():
#                print resource_name, ":"
                for field_name, field in resource.fields.items():
#                    print "   ", field_name, " ", field
                    if hasattr(resource._meta, "example_class"):
                        args.append((resource_name, resource, field_name, field))

            return args

        @staticmethod
        def generate_test_name(resource_name, resource, field_name, field):
            return "_".join([resource_name, field_name])

        @staticmethod
        def setUp(self, *args, **kwargs):
            self.client = Client()
            user_setUp(self, *args, **kwargs)
            

    class TestResourceFields(TestCase):
        __metaclass__ = create_multi_meta(UnderResourceFields)

    return TestResourceFields
