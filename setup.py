
import os
import sys
from shutil import rmtree
from setuptools import setup, find_packages


exclude = ["forms_builder/example_project/dev.db",
           "forms_builder/example_project/local_settings.py"]
exclude = dict([(e, None) for e in exclude])
for e in exclude:
    if e.endswith(".py"):
        try:
            os.remove("%sc" % e)
        except:
            pass
    try:
        with open(e, "r") as f:
            exclude[e] = (f.read(), os.stat(e))
        os.remove(e)
    except Exception:
        pass

if sys.argv[:2] == ["setup.py", "bdist_wheel"]:
    # Remove previous build dir when creating a wheel build,
    # since if files have been removed from the project,
    # they'll still be cached in the build dir and end up
    # as part of the build, which is unexpected.
    try:
        rmtree("build")
    except:
        pass

try:
    setup(
        name = "django-forms-builder",
        version = __import__("forms_builder").__version__,
        author = "Stephen McDonald",
        author_email = "stephen.mc@gmail.com",
        description = ("A Django reusable app providing the ability for "
                       "admin users to create their own forms and report "
                       "on their collected data."),
        long_description = open("README.rst").read(),
        license = "BSD",
        url = "http://github.com/stephenmcd/django-forms-builder",
        zip_safe = False,
        include_package_data = True,
        packages = find_packages(),
        install_requires = [
            "sphinx-me >= 0.1.2",
            "unidecode",
            "django-email-extras >= 0.2",
            "django >= 1.8, < 2.1",
            "future <= 0.15.0",
        ],
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Framework :: Django",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Internet :: WWW/HTTP :: Site Management",
        ]
    )
finally:
    for e in exclude:
        if exclude[e] is not None:
            data, stat = exclude[e]
            try:
                with open(e, "w") as f:
                    f.write(data)
                os.chown(e, stat.st_uid, stat.st_gid)
                os.chmod(e, stat.st_mode)
            except:
                pass
