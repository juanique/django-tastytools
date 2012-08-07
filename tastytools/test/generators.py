# -*- coding: utf-8 -*-
import datetime
import os
import random
import re
import string
import uuid
from decimal import Decimal
from django.utils.timezone import now, is_naive, utc

# backporting os.path.relpath, only availabe in python >= 2.6
try:
    relpath = os.path.relpath
except AttributeError:

    def relpath(path, start=os.curdir):
        """Return a relative version of a path"""

        if not path:
            raise ValueError("no path specified")

        start_list = os.path.abspath(start).split(os.path.sep)
        path_list = os.path.abspath(path).split(os.path.sep)

        # Work out how much of the filepath is shared by start and path.
        i = len(os.path.commonprefix([start_list, path_list]))

        rel_list = [os.path.pardir] * (len(start_list) - i) + path_list[i:]
        if not rel_list:
            return os.curdir
        return os.path.join(*rel_list)


class GeneratorException(Exception):
    pass


class IGNORE_EMPTY(object):
    pass


class Generator(object):
    coerce_type = staticmethod(lambda x: x)
    empty_value = None
    empty_p = 0

    def __init__(self, empty_p=None, empty_value=IGNORE_EMPTY, coerce=None):
        if empty_p is not None:
            self.empty_p = empty_p
        if empty_value is not IGNORE_EMPTY:
            self.empty_value = empty_value
        if coerce is not None:
            self.coerce_type = coerce

    def coerce(self, value):
        return self.coerce_type(value)

    def generate(self):
        raise NotImplementedError

    def get_value(self):
        if random.random() < self.empty_p:
            return self.empty_value
        value = self.generate()
        return self.coerce(value)


class StaticGenerator(Generator):
    def __init__(self, value, *args, **kwargs):
        self.value = value
        super(StaticGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        return self.value


class CallableGenerator(Generator):
    def __init__(self, value, args=None, kwargs=None, *xargs, **xkwargs):
        self.value = value
        self.args = args or ()
        self.kwargs = kwargs or {}
        super(CallableGenerator, self).__init__(*xargs, **xkwargs)

    def generate(self):
        return self.value(*self.args, **self.kwargs)


class UUIDGenerator(Generator):
    def __init__(self, max_length=None, **kwargs):
        self.max_length = max_length
        super(UUIDGenerator, self).__init__(**kwargs)

    def generate(self):
        value = unicode(uuid.uuid1())
        if self.max_length is not None:
            value = value[:self.max_length]
        return value


class StringGenerator(Generator):
    coerce_type = unicode
    singleline_chars = string.letters + u' '
    multiline_chars = singleline_chars + u'\n'

    def __init__(self, chars=None, multiline=False, min_length=1,
            max_length=1000, *args, **kwargs):
        assert min_length >= 0
        assert max_length >= 0
        self.min_length = min_length
        self.max_length = max_length
        if chars is None:
            if multiline:
                self.chars = self.multiline_chars
            else:
                self.chars = self.singleline_chars
        else:
            self.chars = chars
        super(StringGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        length = random.randint(self.min_length, self.max_length)
        value = u''
        for x in xrange(length):
            value += random.choice(self.chars)
        return value


class SlugGenerator(StringGenerator):
    def __init__(self, chars=None, *args, **kwargs):
        if chars is None:
            chars = string.ascii_lowercase + string.digits + '-'
        super(SlugGenerator, self).__init__(
                chars, multiline=False, *args, **kwargs)


class LoremGenerator(Generator):
    coerce_type = unicode
    common = True
    count = 3
    method = 'b'

    def __init__(self, count=None, method=None, common=None, max_length=None,
            *args, **kwargs):
        if count is not None:
            self.count = count
        if method is not None:
            self.method = method
        if common is not None:
            self.common = common
        self.max_length = max_length
        super(LoremGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        from django.contrib.webdesign.lorem_ipsum import paragraphs, sentence,\
            words
        if self.method == 'w':
            lorem = words(self.count, common=self.common)
        elif self.method == 's':
            lorem = u' '.join([sentence()
                for i in xrange(self.count)])
        else:
            paras = paragraphs(self.count, common=self.common)
            if self.method == 'p':
                paras = ['<p>%s</p>' % p for p in paras]
            lorem = u'\n\n'.join(paras)
        if self.max_length:
            length = random.randint(self.max_length / 10, self.max_length)
            lorem = lorem[:max(1, length)]
        return lorem.strip()


class LoremSentenceGenerator(LoremGenerator):
    method = 's'


class LoremHTMLGenerator(LoremGenerator):
    method = 'p'


class LoremWordGenerator(LoremGenerator):
    count = 7
    method = 'w'


class IntegerGenerator(Generator):
    coerce_type = int
    min_value = - 10 ** 5
    max_value = 10 ** 5

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        if min_value is not None:
            self.min_value = min_value
        if max_value is not None:
            self.max_value = max_value
        super(IntegerGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        value = random.randint(self.min_value, self.max_value)
        return value


class SmallIntegerGenerator(IntegerGenerator):
    min_value = -2 ** 7
    max_value = 2 ** 7 - 1


class PositiveIntegerGenerator(IntegerGenerator):
    min_value = 0


class PositiveSmallIntegerGenerator(SmallIntegerGenerator):
    min_value = 0


class FloatGenerator(Generator):
    coerce_type = float
    max_digits = 24
    decimal_places = 10

    def __init__(self, max_digits=None, decimal_places=None, *args, **kwargs):
        if max_digits is not None:
            self.max_digits = max_digits
        if decimal_places is not None:
            self.decimal_places = decimal_places
        super(FloatGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        maxint = 10 ** self.max_digits - 1
        value = (
            float(random.randint(-maxint, maxint)) /
            10 ** self.decimal_places)
        return value


class ChoiceGenerator(Generator):
    choices = []

    def __init__(self, choices=None, *args, **kwargs):
        if choices is not None:
            self.choices = choices
        super(ChoiceGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        return random.choice(self.choices)


class BooleanGenerator(ChoiceGenerator):
    choices = (True, False)


class NullBooleanGenerator(BooleanGenerator):
    empty_p = 1 / 3.0


class DateTimeGenerator(Generator):
    min_date = now() - datetime.timedelta(365 * 5)
    max_date = now() + datetime.timedelta(365 * 1)

    def __init__(self, min_date=None, max_date=None, *args, **kwargs):
        if min_date is not None:
            self.min_date = min_date
        if is_naive(self.min_date):
            self.min_date = self.min_date.replace(tzinfo=utc)

        if max_date is not None:
            self.max_date = max_date
        if is_naive(self.max_date):
            self.max_date = self.max_date.replace(tzinfo=utc)

        assert self.min_date < self.max_date
        super(DateTimeGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        diff = self.max_date - self.min_date
        seconds = random.randint(0, diff.days * 3600 * 24 + diff.seconds)
        return self.min_date + datetime.timedelta(seconds=seconds)


class DateGenerator(Generator):
    min_date = datetime.date.today() - datetime.timedelta(365 * 5)
    max_date = datetime.date.today() + datetime.timedelta(365 * 1)

    def __init__(self, min_date=None, max_date=None, *args, **kwargs):
        if min_date is not None:
            self.min_date = min_date
        if max_date is not None:
            self.max_date = max_date
        assert self.min_date < self.max_date
        super(DateGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        diff = self.max_date - self.min_date
        days = random.randint(0, diff.days)
        date = self.min_date + datetime.timedelta(days=days)
        return date


class DecimalGenerator(Generator):
    coerce_type = Decimal

    max_digits = 24
    decimal_places = 10

    def __init__(self, max_digits=None, decimal_places=None, *args, **kwargs):
        if max_digits is not None:
            self.max_digits = max_digits
        if decimal_places is not None:
            self.decimal_places = decimal_places
        super(DecimalGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        maxint = 10 ** self.max_digits - 1
        value = (
            Decimal(random.randint(-maxint, maxint)) /
            10 ** self.decimal_places)
        return value


class EmailGenerator(StringGenerator):
    chars = string.ascii_lowercase

    def __init__(self, chars=None, max_length=30, tlds=None, *args, **kwargs):
        assert max_length >= 6
        if chars is not None:
            self.chars = chars
        self.tlds = tlds
        super(EmailGenerator, self).__init__(self.chars, max_length=max_length,
                *args, **kwargs)

    def generate(self):
        maxl = self.max_length - 2
        if self.tlds:
            tld = random.choice(self.tlds)
        elif maxl > 4:
            tld = StringGenerator(
                    self.chars, min_length=3, max_length=3).generate()
        maxl -= len(tld)
        assert maxl >= 2

        name = StringGenerator(
                self.chars, min_length=1, max_length=maxl - 1).generate()
        maxl -= len(name)
        domain = StringGenerator(
                self.chars, min_length=1, max_length=maxl).generate()
        return '%s@%s.%s' % (name, domain, tld)


class URLGenerator(StringGenerator):
    chars = string.ascii_lowercase
    protocol = 'http'
    tlds = ()

    def __init__(self, chars=None, max_length=30, protocol=None, tlds=None,
        *args, **kwargs):
        if chars is not None:
            self.chars = chars
        if protocol is not None:
            self.protocol = protocol
        if tlds is not None:
            self.tlds = tlds
        assert max_length > (
            len(self.protocol) + len('://') +
            1 + len('.') +
            max([2] + [len(tld) for tld in self.tlds if tld]))
        super(URLGenerator, self).__init__(
            chars=self.chars, max_length=max_length, *args, **kwargs)

    def generate(self):
        maxl = self.max_length - len(self.protocol) - 4  # len(://) + len(.)
        if self.tlds:
            tld = random.choice(self.tlds)
            maxl -= len(tld)
        else:
            tld_max_length = 3 if maxl >= 5 else 2
            tld = StringGenerator(self.chars,
                min_length=2, max_length=tld_max_length).generate()
            maxl -= len(tld)
        domain = StringGenerator(chars=self.chars, max_length=maxl).generate()
        return u'%s://%s.%s' % (self.protocol, domain, tld)


class IPAddressGenerator(Generator):
    coerce_type = unicode

    def generate(self):
        return '.'.join([unicode(part) for part in [
            IntegerGenerator(min_value=1, max_value=254).generate(),
            IntegerGenerator(min_value=0, max_value=254).generate(),
            IntegerGenerator(min_value=0, max_value=254).generate(),
            IntegerGenerator(min_value=1, max_value=254).generate(),
        ]])


class TimeGenerator(Generator):
    def generate(self):
        return datetime.time(
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59),
            random.randint(0, 999999),
        )


class FilePathGenerator(Generator):
    coerce_type = unicode

    def __init__(self, path, match=None, recursive=False, max_length=None,
            *args, **kwargs):
        self.path = path
        self.match = match
        self.recursive = recursive
        self.max_length = max_length
        super(FilePathGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        filenames = []
        if self.match:
            match_re = re.compile(self.match)
        if self.recursive:
            for root, dirs, files in os.walk(self.path):
                for f in files:
                    if self.match is None or self.match.search(f):
                        f = os.path.join(root, f)
                        filenames.append(f)
        else:
            try:
                for f in os.listdir(self.path):
                    full_file = os.path.join(self.path, f)
                    if os.path.isfile(full_file) and \
                        (self.match is None or match_re.search(f)):
                        filenames.append(full_file)
            except OSError:
                pass
        if self.max_length:
            filenames = [fn for fn in filenames if len(fn) <= self.max_length]
        return random.choice(filenames)


class MediaFilePathGenerator(FilePathGenerator):
    '''
    Generates a valid filename of an existing file from a subdirectory of
    ``settings.MEDIA_ROOT``. The returned filename is relative to
    ``MEDIA_ROOT``.
    '''
    def __init__(self, path='', *args, **kwargs):
        from django.conf import settings
        path = os.path.join(settings.MEDIA_ROOT, path)
        super(MediaFilePathGenerator, self).__init__(path, *args, **kwargs)

    def generate(self):
        from django.conf import settings
        filename = super(MediaFilePathGenerator, self).generate()
        filename = relpath(filename, settings.MEDIA_ROOT)
        return filename


# TODO: try to get this thing out of here
class InstanceGenerator(Generator):
    '''
    Naive support for ``limit_choices_to``. It assignes specified value to
    field for dict items that have one of the following form::

        fieldname: value
        fieldname__exact: value
        fieldname__iexact: value
    '''
    def __init__(self, mockup, limit_choices_to=None, *args, **kwargs):
        self.mockup = mockup
        from django.db.models import Q
        if not isinstance(limit_choices_to, Q):  # no Q support
            limit_choices_to = limit_choices_to or {}
            for lookup, value in limit_choices_to.items():
                bits = lookup.split('__')
                if len(bits) == 1 or \
                    len(bits) == 2 and bits[1] in ('exact', 'iexact'):
                    params = {
                        bits[0]: StaticGenerator(value),
                    }
                    self.mockup.update_fieldname_generator(**params)
        super(InstanceGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        return self.mockup.create()[0]


class MultipleInstanceGenerator(InstanceGenerator):
    empty_value = []

    def __init__(self, *args, **kwargs):
        self.min_count = kwargs.pop('min_count', 1)
        self.max_count = kwargs.pop('max_count', 10)
        super(MultipleInstanceGenerator, self).__init__(*args, **kwargs)

    def generate(self):
        instances = []
        for i in xrange(random.randint(self.min_count, self.max_count)):
            instances.append(
                super(MultipleInstanceGenerator, self).generate())
        return instances


class InstanceSelector(Generator):
    '''
    Select one or more instances from a queryset.
    '''
    empty_value = []

    def __init__(self, queryset, min_count=None, max_count=None, fallback=None,
        limit_choices_to=None, *args, **kwargs):
        from django.db.models.query import QuerySet
        from django.db.models import Q
        if not isinstance(queryset, QuerySet):
            queryset = queryset._default_manager.all()
        if isinstance(limit_choices_to, Q):
            self.queryset = queryset.filter(limit_choices_to)
        else:
            limit_choices_to = limit_choices_to or {}
            self.queryset = queryset.filter(**limit_choices_to)
        self.fallback = fallback
        self.min_count = min_count
        self.max_count = max_count
        super(InstanceSelector, self).__init__(*args, **kwargs)

    def generate(self):
        if self.max_count is None:
            try:
                return self.queryset.order_by('?')[0]
            except IndexError:
                return self.fallback
        else:
            min_count = self.min_count or 0
            count = random.randint(min_count, self.max_count)
            return self.queryset.order_by('?')[:count]


#
# Field coupled generators
#
class FieldGenerator(Generator):
    def __init__(self, field, **kwargs):
        empty_p = kwargs.pop('empty_p', None)
        coerce = kwargs.pop('coerce', None)
        self.field = field
        self.kwargs = kwargs
        super(FieldGenerator, self).__init__(empty_p=empty_p, coerce=coerce)

    def get_generator(self, field, **kwargs):
        raise NotImplementedError

    def generate(self):
        if not hasattr(self, '_generator'):
            self._generator = self.get_generator(self.field, **self.kwargs)
        return self._generator.generate()


class ChoiceFieldGenerator(FieldGenerator):
    def get_generator(self, field, *args, **kwargs):
        return ChoiceGenerator([k for k, v in field.choices])


class FilePathFieldGenerator(FieldGenerator):
    def get_generator(self, field, **kwargs):
        return FilePathGenerator(
            path=field.path, match=field.match, recursive=field.recursive,
            max_length=field.max_length)


class CharFieldGenerator(FieldGenerator):
    def get_generator(self, field, **kwargs):
        max_length = field.max_length
        if max_length < 15:
            return StringGenerator(max_length=max_length)
        return LoremSentenceGenerator(common=False, max_length=max_length)


class DecimalFieldGenerator(FieldGenerator):
    def get_generator(self, field, **kwargs):
        return DecimalGenerator(
            decimal_places=field.decimal_places,
            max_digits=field.max_digits)


class BigIntegerFieldGenerator(FieldGenerator):
    def get_generator(self, field, **kwargs):
        return IntegerGenerator(min_value=-field.MAX_BIGINT - 1,
                max_value=field.MAX_BIGINT)
