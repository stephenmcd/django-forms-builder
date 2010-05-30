Introduction
------------

A Django reusable app providing the ability for admin users to create their own forms within the admin interface drawing from a set of fields defined by the developer.

Installation
------------

Checkout the source and run ``python setup.py install``. You can then add ``email_extras`` to your ``INSTALLED_APPS`` and ``forms_builder.urls`` to your url conf.

How It Works
------------

Two models are defined in forms_builder.models - ``BuiltForm`` and ``BuiltFormSubmission`` which represent a user created form and a submission to that form respectively. ``BuiltForm`` contains two special fields called ``mandatory_extra_fields`` and ``optional_extra_fields``. These are present in the admin interface as a list of checkboxes derived from all the fields on the ``BuiltFormSubmission`` model that have the keyword attribute ``blank`` set to ``True``. The difference between these two sets of fields is whether the fields are mandatory for the website user submitting the form.

The actual form that gets displayed on the website is a ``ModelForm`` for ``BuiltFormSubmission`` and any of the fields within ``mandatory_extra_fields`` and ``optional_extra_fields`` that aren't selected for a given ``BuiltForm`` are excluded from the form on the website. The developer has the ability to define fields that are always present in the website form by not setting the ``blank`` attribute to ``True`` on the relevant fields of the ``BuiltFormSubmission`` model.

Configuration
-------------

As described above, configuration of website form fields is done entirely on the ``BuiltFormSubmission`` model. Fields with a ``blank`` attribute set to ``True`` will be available as extra fields, and all other fields will always be present on the website form.

There are also two settings you can configure in your project's ``settings`` module:

    * ``FORMS_BUILDER_EMAIL_TO`` - An email address that will be sent an email upon each form submission if the ``send_email`` field is set to ``True`` by the admin user for the given ``BuiltForm``.

    * ``FORMS_BUILDER_UPLOAD_TO`` - The location in your ``MEDIA_ROOT`` that files will be saved to if any ``FileField`` or ``ImageField`` fields are defined on your ``BuiltFormSubmission`` model. These files will also be attached to the email if it is sent.

