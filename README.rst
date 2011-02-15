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

Installation
============

Assuming you have `setuptools`_ installed, the easiest method is to install 
directly from pypi by running the following command::

    $ easy_install -U django-forms-builder

Otherwise you can check out the source directly and install it via::

    $ python setup.py install

Once installed you can then add ``forms_builder.forms`` to your 
``INSTALLED_APPS`` and ``forms_builder.forms.urls`` to your url conf.

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

.. _`setuptools`: http://pypi.python.org/pypi/setuptools

