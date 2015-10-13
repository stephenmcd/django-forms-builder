# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='template_name',
            field=models.CharField(max_length=200, blank=True, help_text='An alternate template to render form detail.', null=True, verbose_name='Template name'),
        ),
        migrations.AlterField(
            model_name='form',
            name='email_from',
            field=models.EmailField(max_length=254, blank=True, help_text='The address the email will be sent from', verbose_name='From address'),
        ),
    ]
