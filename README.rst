Introduction
============

A Django reusable app providing the ability for admin users to create their 
own forms within the admin interface drawing from a range of field widgets 
such as regular text fields, drop-down lists and file uploads. Options are 
also provided for controlling who gets sent email notifications when a form 
is submitted. All form entries are made available in the admin via CSV export.

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

.. _`setuptools`: http://pypi.python.org/pypi/setuptools

