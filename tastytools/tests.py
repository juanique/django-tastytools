from django.utils import unittest
from django.test.client import RequestFactory
from api import Api
from example import resources1, resources2, resources3
from validation import FieldsValidation


class ApiTestCase(unittest.TestCase):

    def setUp(self):

        resources = [resources1.Test_1_2_Resource, resources1.Test_1_3_Resource()]
        modules = [resources2, resources3]

        self.api = Api()
        self.api.register(resources1.Test_1_1_Resource())
        self.api.register(resources=resources)
        self.api.register(modules=modules)
        #self.factory = RequestFactory()
        #self.request = self.factory.get("")
        
    def _assert_in_registry(self, resource_names):
        for resource_name in resource_names:
            try:
                assert resource_name in self.api._registry 
            except:
                print resource_name
                raise

    def test_resource_importing(self):
        """The Api class is able to import a single resource"""
        self._assert_in_registry(["test_1_1"])

    def test_resource_list_importing(self):
        """The Api class is able to import a list of resources"""
        self._assert_in_registry(["test_1_2", "test_1_3"])
        
    def test_module_list_importing(self):
        """The Api class is able to import all resources from listed modules"""
        self._assert_in_registry(["test_2_1", "test_2_2", "test_2_3"])
        self._assert_in_registry(["test_3_1", "test_3_2", "test_3_3"])


class FieldsValidationTest(unittest.TestCase):
    def test_parse_methods_key(self):
        validation = FieldsValidation()
        key = "required_post"
        #value = ['field1', 'field2']

        methods = validation.parse_methods_key(key, 'required')
        self.assertEqual(['POST'], methods)

    def test_map_method_validation(self):
        validation = FieldsValidation()
        fields = ['field1', 'field2']
        methods = ["POST", "PUT", "GET", "DELETE"]
        target = {}
        validation.map_method_validations(target, fields, methods)

        expected = {
                'POST': ['field1', 'field2'],
                'GET': ['field1', 'field2'],
                'PUT': ['field1', 'field2'],
                'DELETE': ['field1', 'field2'],
                }

        self.assertEqual(expected, target)

        validation.map_method_validations(target, ['field3'], ['PUT', 'POST'])

        expected = {
                'POST': ['field1', 'field2', 'field3'],
                'GET': ['field1', 'field2'],
                'PUT': ['field1', 'field2', 'field3'],
                'DELETE': ['field1', 'field2'],
                }

        self.assertEqual(expected, target)

    def test_fieldsvalid_constructor(self):
        validation = FieldsValidation(required=['f1', 'f2'],
                                      validated=['f1', 'f3'],
                                      required_post_get=['f4'],
                                      validated_put=['f5'])

        expected_required = {
                'POST': ['f1', 'f2', 'f4'],
                'GET': ['f1', 'f2', 'f4'],
                'PUT': ['f1', 'f2'],
                'DELETE': ['f1', 'f2'],
                'PATCH': ['f1', 'f2'],
                }

        expected_validated = {
                'POST': ['f1', 'f3'],
                'GET': ['f1', 'f3'],
                'PUT': ['f1', 'f3', 'f5'],
                'DELETE': ['f1', 'f3'],
                'PATCH': ['f1', 'f3'],
                }

        self.assertEqual(expected_validated, validation.validated_fields)
        self.assertEqual(expected_required, validation.required_fields)
