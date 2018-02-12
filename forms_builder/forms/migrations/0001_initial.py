# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from forms_builder.forms import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=200, verbose_name='Label')),
                ('slug', models.SlugField(default='', max_length=100, verbose_name='Slug', blank=True)),
                ('field_type', models.IntegerField(verbose_name='Type', choices=[(1, 'Single line text'), (2, 'Multi line text'), (3, 'Email'), (13, 'Number'), (14, 'URL'), (4, 'Check box'), (5, 'Check boxes'), (6, 'Drop down'), (7, 'Multi select'), (8, 'Radio buttons'), (9, 'File upload'), (10, 'Date'), (11, 'Date/time'), (15, 'Date of birth'), (12, 'Hidden')])),
                ('required', models.BooleanField(default=True, verbose_name='Required')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
                ('choices', models.CharField(help_text='Comma separated options where applicable. If an option itself contains commas, surround the option starting with the `character and ending with the ` character.', max_length=1000, verbose_name='Choices', blank=True)),
                ('default', models.CharField(max_length=2000, verbose_name='Default value', blank=True)),
                ('placeholder_text', models.CharField(max_length=100, null=True, verbose_name='Placeholder Text', blank=True)),
                ('help_text', models.CharField(max_length=100, verbose_name='Help text', blank=True)),
                ('order', models.IntegerField(null=True, verbose_name='Order', blank=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
                'verbose_name': 'Field',
                'verbose_name_plural': 'Fields',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_id', models.IntegerField()),
                ('value', models.CharField(max_length=2000, null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Form field entry',
                'verbose_name_plural': 'Form field entries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('slug', models.SlugField(verbose_name='Slug', unique=True, max_length=100, editable=False)),
                ('intro', models.TextField(verbose_name='Intro', blank=True)),
                ('button_text', models.CharField(default='Submit', max_length=50, verbose_name='Button text')),
                ('response', models.TextField(verbose_name='Response', blank=True)),
                ('redirect_url', models.CharField(help_text='An alternate URL to redirect to after form submission', max_length=200, null=True, verbose_name='Redirect url', blank=True)),
                ('status', models.IntegerField(default=2, verbose_name='Status', choices=[(1, 'Draft'), (2, 'Published')])),
                ('publish_date', models.DateTimeField(help_text="With published selected, won't be shown until this time", null=True, verbose_name='Published from', blank=True)),
                ('expiry_date', models.DateTimeField(help_text="With published selected, won't be shown after this time", null=True, verbose_name='Expires on', blank=True)),
                ('login_required', models.BooleanField(default=False, help_text='If checked, only logged in users can view the form', verbose_name='Login required')),
                ('send_email', models.BooleanField(default=True, help_text='If checked, the person entering the form will be sent an email', verbose_name='Send email')),
                ('email_from', models.EmailField(help_text='The address the email will be sent from', max_length=75, verbose_name='From address', blank=True)),
                ('email_copies', models.CharField(help_text='One or more email addresses, separated by commas', max_length=200, verbose_name='Send copies to', blank=True)),
                ('email_subject', models.CharField(max_length=200, verbose_name='Subject', blank=True)),
                ('email_message', models.TextField(verbose_name='Message', blank=True)),
                ('sites', models.ManyToManyField(default=[settings.SITE_ID], related_name='forms_form_forms', to='sites.Site')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Form',
                'verbose_name_plural': 'Forms',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry_time', models.DateTimeField(verbose_name='Date/time')),
                ('form', models.ForeignKey(related_name='entries', to='forms.Form', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Form entry',
                'verbose_name_plural': 'Form entries',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='fieldentry',
            name='entry',
            field=models.ForeignKey(related_name='fields', to='forms.FormEntry', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='field',
            name='form',
            field=models.ForeignKey(related_name='fields', to='forms.Form', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
