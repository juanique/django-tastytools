from tastypie import fields


class TastyToolsField(object):
    def __init__(self, parent_class, *args, **kwargs):
        self.final = kwargs.get("final", False)
        try:
            del kwargs['final']
        except:
            pass
        parent_class.__init__(self, *args, **kwargs)

class CharField(TastyToolsField, fields.CharField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.CharField, *args, **kwargs)

class FileField(TastyToolsField, fields.FileField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.FileField, *args, **kwargs)

class IntegerField(TastyToolsField, fields.IntegerField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.IntegerField, *args, **kwargs)

class FloatField(TastyToolsField, fields.FloatField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.FloatField, *args, **kwargs)

class DecimalField(TastyToolsField, fields.DecimalField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.DecimalField, *args, **kwargs)

class BooleanField(TastyToolsField, fields.BooleanField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.BooleanField, *args, **kwargs)

class ListField(TastyToolsField, fields.ListField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.ListField, *args, **kwargs)

class DictField(TastyToolsField, fields.DictField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.DictField, *args, **kwargs)

class DateField(TastyToolsField, fields.DateField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.DateField, *args, **kwargs)

class DateTimeField(TastyToolsField, fields.DateTimeField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.DateTimeField, *args, **kwargs)

class ToOneField(TastyToolsField, fields.ToOneField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.ToOneField, *args, **kwargs)

class ToManyField(TastyToolsField, fields.ToManyField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.ToManyField, *args, **kwargs)

class TimeField(TastyToolsField, fields.TimeField):
    def __init__(self, *args, **kwargs):
        TastyToolsField.__init__(self, fields.TimeField, *args, **kwargs)


