from tastypie.resources import ModelResource
from ..models import Test

class Test_2_1_Resource(ModelResource):
    class Meta:
        resource_name = "test_2_1"
        queryset = Test.objects.all()
        
class Test_2_2_Resource(ModelResource):
    class Meta:
        resource_name = "test_2_2"
        queryset = Test.objects.all()
    
class Test_2_3_Resource(ModelResource):
    class Meta:
        resource_name = "test_2_3"
        queryset = Test.objects.all()