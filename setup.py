
import os
import sys
from shutil import rmtree
from setuptools import setup, find_packages


version = __import__('forms_builder').__version__

if sys.argv[-1] == 'publish':
    if os.path.exists("build"):
        rmtree("build")
    os.system('python setup.py bdist_wheel upload -r natgeo')
    print("You probably want to also tag the version now:")
    print("  python setup.py tag")
    sys.exit()
elif sys.argv[-1] == 'tag':
    cmd = "git tag -a %s -m 'version %s';git push --tags" % (version, version)
    os.system(cmd)
    sys.exit()

setup(
    name="django-forms-builder",
    version=__import__("forms_builder").__version__,
    author="Stephen McDonald",
    author_email="stephen.mc@gmail.com",
    description=("A Django reusable app providing the ability for "
                   "admin users to create their own forms and report "
                   "on their collected data."),
    long_description=open("README.rst").read(),
    license="BSD",
    url="http://github.com/stephenmcd/django-forms-builder",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['*example*', ]),
    install_requires=[
        "unidecode",
        "django-email-extras >= 0.2",
        "future >= 0.16.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ]
)
