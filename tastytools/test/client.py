from django.test import Client as DjangoClient
from django.core.serializers import json
from django.test.client import MULTIPART_CONTENT, BOUNDARY, encode_multipart, FakePayload
from django.utils.http import urlencode
from django.utils import simplejson
from urlparse import urlparse

class Client(DjangoClient):

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)

    def patch_request(self, path, data={}, follow=False, content_type=MULTIPART_CONTENT, **extra):
        "Construct a PATCH request."

        if content_type is MULTIPART_CONTENT:
            post_data = encode_multipart(BOUNDARY, data)
        else:
            post_data = data

        # Make `data` into a querystring only if it's not already a string. If
        # it is a string, we'll assume that the caller has already encoded it.
        query_string = None
        if not isinstance(data, basestring):
            query_string = urlencode(data, doseq=True)

        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE':   content_type,
            'PATH_INFO':      self._get_path(parsed),
            'QUERY_STRING':   query_string or parsed[4],
            'REQUEST_METHOD': 'PATCH',
            'wsgi.input':     FakePayload(post_data),
        }
        r.update(extra)
        return self.request(**r)

    def patch(self, path, data={}, follow=False, content_type="application/json", **extra):
        """
        Send a resource patch to the server using PATCH.
        """
        if type(data) == dict and content_type == "application/json":
            data = simplejson.dumps(data, cls=json.DjangoJSONEncoder)

        response = self.patch_request(path, data=data, content_type=content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response


    def post(self, path, data={}, content_type='application/json', follow=False,
             parse=None, **extra):
        """
        Changes default content type to applcation/json. And automatically sets data
        to a raw json string.
        """

        if type(data) == dict and content_type == "application/json":
            data = simplejson.dumps(data, cls=json.DjangoJSONEncoder)

        response = super(Client, self).post(path, data, content_type, follow=False, **extra)

        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except:
                response.data = None

        return response

    def put(self, path, data={}, content_type='application/json', follow=False,
             **extra):
        """
        Changes default content type to applcation/json. And automatically sets data
        to a raw json string.
        """

        if type(data) == dict:
            data = simplejson.dumps(data, cls=json.DjangoJSONEncoder)

        return super(Client, self).put(path, data, content_type, **extra)


    def get(self, path, data={}, follow=False, parse=None, **extra):
        response = super(Client, self).get(path, data, follow, **extra)

        if parse == "json":
            try:
                response.data = simplejson.loads(response.content)
            except Exception, e:
                print e
                response.data = None

        return response

    def rpc(self, method, *args, **kwargs):
        post_data =  {
            "jsonrpc": "2.0", 
            "method": method, 
            "params" : kwargs,
            "id" : 1,
        }

        return self.post("/api/rpc/", post_data, parse='json')

class MultiTestCase(object):
    pass


def create_multi_meta(multi_class):
    class MetaTest(type):

        def __new__(cls, name, bases, attrs):
            funcs = [test for test in dir(multi_class) if test.startswith("multi_")]

            def doTest(test, *args):
                def test_func(self):
                    ut = multi_class()
                    getattr(ut, test)(self,*args)
                return test_func

            for func in funcs:
                for args in multi_class.generate_arguments():
                    test_func_name = 'test_gen_%s_%s' % (func,multi_class.generate_test_name(*args))
                    attrs[test_func_name] = doTest(func, *args)
            return type.__new__(cls, name, bases, attrs)

    return MetaTest

