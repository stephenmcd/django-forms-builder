
from distutils.core import setup
 
 
setup(
    name = "django-forms-builder",
    version = __import__("forms_builder").__version__,
    author = "Stephen McDonald",
    author_email = "stephen.mc@gmail.com",
    description = ("A Django reusable app providing the ability for admin "
        "users to create their own forms within the admin interface drawing "
        "from a set of fields defined by the developer."),
    long_description = open("README.rst").read(),
    url = "http://bitbucket.org/citrus/django-forms-builder",
    packages = ["forms_builder",],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ]
)

