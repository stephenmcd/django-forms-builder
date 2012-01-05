Introduction
============

A Django reusable app providing the ability for admin users to create their
own forms within the admin interface drawing from a range of field widgets
such as regular text fields, drop-down lists and file uploads. Options are
also provided for controlling who gets sent email notifications when a form
is submitted. All form entries are made available in the admin via CSV export.

HTML5 Features
==============

The folliwng HTML5 form features are supported.

* ``placeholder`` attributes
* ``required`` attributes
* ``email`` fields
* ``date`` fields
* ``datetime`` fields
* ``number`` fields
* ``url`` fields

Installation
============

The easiest way to install django-forms-builder is directly from PyPi using
`pip`_ or `setuptools`_ by running the respective command below::

    $ pip install -U django-forms-builder

or::

    $ easy_install -U django-forms-builder

Otherwise you can download django-forms-builder and install it directly
from source::

    $ python setup.py install

Project Configuration
=====================

Once installed you can configure your project to use django-forms-builder
with the following steps.

Add ``forms_builder.forms`` to ``INSTALLED_APPS`` in your project's
``settings`` module::

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'forms_builder.forms',
    )

Then add ``forms_builder.forms.urls`` to your project's ``urls`` module::

    from django.conf.urls.defaults import patterns, include, url
    import forms_builder.forms.urls # add this import

    from django.contrib import admin
    admin.autodiscover()

    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^forms/', include(forms_builder.forms.urls)),
    )

Finally, sync your database::

    $ python manage.py syncdb

Usage
=====

Once installed and configured for your project just go to the admin page for your project and you will see a new Forms section. In this you can create and edit forms.


File Uploads
============

It's possible for admin users to create forms that allow file uploads which
can be accessed via a download URL for each file that is provided in the
CSV export. By default these uploaded files are stored in an obscured
location under your project's ``MEDIA_ROOT`` directory but ideally the
should be stored somewhere inaccessible to the public. To set the location
where files are stored to be somewhere outside of your project's
``MEDIA_ROOT`` directory you just need to define the
``FORMS_BUILDER_UPLOAD_ROOT`` setting in your project's ``settings``
module. Its value should be an absolute path on the web server that isn't
accessible to the public.

Configuration
=============

The following settings can be defined in your project's ``settings`` module.

* ``FORMS_BUILDER_FIELD_MAX_LENGTH`` - Maximum allowed length for field values. Defaults to ``2000``
* ``FORMS_BUILDER_LABEL_MAX_LENGTH`` - Maximum allowed length for field labels. Defaults to ``20``
* ``FORMS_BUILDER_UPLOAD_ROOT`` - The absolute path where files will be uploaded to. Defaults to ``None``
* ``FORMS_BUILDER_USE_HTML5`` - Boolean controlling whether HTML5 form fields are used. Defaults to ``True``
* ``FORMS_BUILDER_USE_SITES`` - Boolean controlling whether forms are associated to Django's Sites framework. Defaults to ``"django.contrib.sites" in settings.INSTALLED_APPS``
* ``FORMS_BUILDER_CHOICES_QUOTE`` - Char to start a quoted choice with. Defaults to the backtick char: `
* ``FORMS_BUILDER_CHOICES_UNQUOTE`` - Char to end a quoted choice with. Defaults to the backtick char: `
* ``FORMS_BUILDER_CSV_DELIMITER`` - Char to use as a field delimiter when exporting form responses as CSV. Defaults to a comma: ,

Signals
=======

Two signals are provided for hooking into different states of the form
submission process.


* ``form_invalid(sender=request, form=form)`` - Sent when the form is submitted with invalid data.
* ``form_valid(sender=request, form=form, entry=entry)`` - Sent when the form is submitted with valid data.

For each signal the sender argument is the current request. Both signals
receive a ``form`` argument is given which is the ``FormForForm``
instance, a ``ModelForm`` for the ``FormEntry`` model.

The ``form_valid`` signal also receives a ``entry`` argument, which is
the ``FormEntry`` model instance created.

.. _`pip`: http://www.pip-installer.org/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
