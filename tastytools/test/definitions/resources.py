from django.test import TestCase
from tastytools.test.resources import TestData
from tastytools.test.client import Client, MultiTestCase, create_multi_meta


def generate(api):
    class UnderResources(MultiTestCase):

        @staticmethod
        def multi_create_test_resource_unicity(self, resource_name, resource):
            resource.create_test_resource()
            all_resources = resource._meta.object_class.objects.all()
            self.assertEqual(1, len(all_resources))

        @staticmethod
        def multi_create_test_resource(self, resource_name, resource):
            #only if resource allows detail GET
            if 'GET' not in resource._meta.detail_allowed_methods:
                return

            client = Client()
            msg = "Could not create test resource for %s" % resource_name

            try:
                resource.create_test_resource()
            except Exception, err:
                msg = "%s: %s - %s"
                msg %= (msg, err.__class__.__name__, err.message)
                self.assertTrue(False, msg)

            get_response = client.get(resource.get_resource_list_uri(),
                parse='json')
            self.assertEqual(1, get_response.data['meta']['total_count'], msg)

        @staticmethod
        def multi_example_data_existence(self, resource_name, resource):
            #Check existence
            for method in ['POST', 'GET']:
                try:
                    if api.resource_allows_method(resource_name, method):
                        example = getattr(resource._meta.example,
                            method.lower())
                        msg = "Example %s data is not a TestData or dict "\
                            "but %s"

                        msg %= (method, example.__class__)
                        is_testdata = issubclass(example.__class__, TestData)
                        is_dict = type(example) == dict
                        self.assertTrue(is_testdata or is_dict, msg)

                except (AttributeError, KeyError), err:
                    message = "Missing example %s data for %s resource.: %s"
                    message %= (method, resource_name, err)
                    self.assertTrue(False, message)

        @staticmethod
        def multi_example_post_data(self, resource_name, resource):
            #We use an authenticated client for testing POST
            client = Client()
            passwd = "OLDKGAS$AFAG"
            profile_res = api.resource('userprofile')
            profile = profile_res.create_test_resource(
                {'password': passwd})
            self.assertTrue(client.login(username=profile[1].email,
                password=passwd))

            #Test POST
            if resource.can_create():
                post_data = resource.get_test_post_data()

                post_response = client.post(resource.get_resource_list_uri(),
                    post_data)

                msg = "Failed to POST example data for resource "\
                    "S: %s. R(%s): %s"
                msg %= (post_data, post_response.status_code,
                        post_response.content)
                self.assertEqual(post_response.status_code, 201, msg)

        @staticmethod
        def multi_example_get_data(self, resource_name, resource):

            #only if resource allows detail GET
            if 'get' not in resource._meta.detail_allowed_methods:
                return

            client = Client()
            if api.resource_allows_method(resource_name, 'GET'):
                uri, res = resource.create_test_resource()
                get_response = client.get(uri, parse='json')
                self.assertEqual(200, get_response.status_code,
                    get_response.data)
                response_dict = get_response.data

                object_keys = set(response_dict.keys())
                expected_keys = set(resource._meta.example.get.keys())

                msg = "GET data does not match the example for resource "\
                    "%s - EXAMPLE: %s vs GET: %s"
                msg %= (resource_name, expected_keys, object_keys)
                self.assertEqual(expected_keys, object_keys, msg)

        @staticmethod
        def multi_declared_example_fields_coherence(self, resource_name,
            resource):

            #only if resource allows detail GET
            if 'GET' not in resource._meta.detail_allowed_methods:
                return

            example_fields = set(resource.example_fields)
            declared_fields = set(resource.declared_fields.keys())

            delta = example_fields - declared_fields
            if len(delta) > 0:
                msg = "%s.%s field appears on the examples but it is "\
                    "not declared."
                msg %= (resource_name, delta.pop())
                self.assertTrue(False, msg)

            delta = declared_fields - example_fields
            if len(delta) > 0:
                msg = "%s.%s field is declared but is missing from examples."
                msg %= (resource_name, delta.pop())
                self.assertTrue(False, msg)

        @staticmethod
        def generate_arguments():
            args = []
            for resource_name, resource in api._registry.items():
                args.append((resource_name, resource))
            return args

        @staticmethod
        def generate_test_name(resource_name, resource):
            return resource_name

    class TestResources(TestCase):
        __metaclass__ = create_multi_meta(UnderResources)

    return TestResources
