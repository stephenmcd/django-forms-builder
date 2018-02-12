# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-27 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0002_auto_20160418_0120'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='custom_form_template',
            field=models.CharField(blank=True, default='forms/includes/built_form.html', help_text='If changed it will user diffrent template to render the form', max_length=200, verbose_name='Render using custom template'),
        ),
    ]