from setuptools import setup, find_packages

setup(
    name="django-tastytools",
    version="0.1.0",
    packages = find_packages(),
    # packages=[
    #     "tastytools",
    #     "tastytools.test",
    #     "tastytools.test.definitions",
    #     "tastytools.api_doc",
    #     "tastytools.api_doc.templatetags",
    # ],
    package_data={
        'tastytools' : [
            '*.*',
            'api_doc/static/js/tastytools/*.*',
            'api_doc/static/js/tastytools/lib/*.*',
            'api_doc/static/js/tastytools/lib/SyntaxHighlighter/*.*',
            'api_doc/static/css/tastytools/*.*',
            'api_doc/static/css/tastytools/lib/*.*',
            'api_doc/static/css/tastytools/lib/SyntaxHighlighter/*.*',
            'api_doc/templates/api_doc/*',
        ]
    },
    long_description="Tools for django-tastypie autotesting and documentation.",
)

