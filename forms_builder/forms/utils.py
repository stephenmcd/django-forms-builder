from os.path import basename
from warnings import warn

from django.template import loader
from django.core.mail import EmailMultiAlternatives, get_connection

from django.template.defaultfilters import slugify as django_slugify
from importlib import import_module

from django.utils.timezone import now
from django.http.request import HttpRequest


def slugify(s):
    """
    Translates unicode into closest possible ascii chars before
    slugifying.
    """
    return django_slugify(str(s))


def unique_slug(manager, slug_field, slug):
    """
    Ensure slug is unique for the given manager, appending a digit
    if it isn't.
    """
    max_length = manager.model._meta.get_field(slug_field).max_length
    slug = slug[:max_length]
    i = 0
    while True:
        if i > 0:
            if i > 1:
                slug = slug.rsplit("-", 1)[0]
            # We need to keep the slug length under the slug fields max length. We need to
            # account for the length that is added by adding a random integer and `-`.
            slug = "%s-%s" % (slug[:max_length - len(str(i)) - 1], i)
        if not manager.filter(**{slug_field: slug}):
            break
        i += 1
    return slug


def split_choices(choices_string):
    """
    Convert a comma separated choices string to a list.
    """
    return [x.strip() for x in choices_string.split(",") if x.strip()]


def html5_field(name, base):
    """
    Takes a Django form field class and returns a subclass of
    it with the given name as its input type.
    """
    return type(str(""), (base, ), {"input_type": name})


def import_attr(path):
    """
    Given a a Python dotted path to a variable in a module,
    imports the module and returns the variable in it.
    """
    module_path, attr_name = path.rsplit(".", 1)
    return getattr(import_module(module_path), attr_name)


class EncryptionFailedError(Exception):
    pass


def addresses_for_key(gpg, key):
    """
    Takes a key and extracts the email addresses for it.
    """
    fingerprint = key["fingerprint"]
    addresses = []
    for key in gpg.list_keys():
        if key["fingerprint"] == fingerprint:
            addresses.extend([
                address.split("<")[-1].strip(">") for address in key["uids"]
                if address
            ])
    return addresses


def send_mail(subject,
              body_text,
              addr_from,
              recipient_list,
              fail_silently=False,
              auth_user=None,
              auth_password=None,
              attachments=None,
              body_html=None,
              html_message=None,
              connection=None,
              headers=None):
    """
    Sends a multipart email containing text and html versions which
    are encrypted for each recipient that has a valid gpg key
    installed.
    """

    # Make sure only one HTML option is specified
    if body_html is not None and html_message is not None:  # pragma: no cover
        raise ValueError("You cannot specify body_html and html_message at "
                         "the same time. Please only use html_message.")

    # Push users to update their code
    if body_html is not None:  # pragma: no cover
        warn(
            "Using body_html is deprecated; use the html_message argument "
            "instead. Please update your code.", DeprecationWarning)
        html_message = body_html

    # Allow for a single address to be passed in.
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]

    connection = connection or get_connection(username=auth_user,
                                              password=auth_password,
                                              fail_silently=fail_silently)

    # Load attachments and create name/data tuples.
    attachments_parts = []
    if attachments is not None:
        for attachment in attachments:
            # Attachments can be pairs of name/data, or filesystem paths.
            if not hasattr(attachment, "__iter__"):
                with open(attachment, "rb") as f:
                    attachments_parts.append((basename(attachment), f.read()))
            else:
                attachments_parts.append(attachment)

    # Send emails - encrypted emails needs to be sent individually, while
    # non-encrypted emails can be sent in one send. So the final list of
    # lists of addresses to send to looks like:
    # [[unencrypted1, unencrypted2, unencrypted3]]
    unencrypted = [addr for addr in recipient_list]
    unencrypted = [unencrypted] if unencrypted else unencrypted

    for addr_list in unencrypted:
        msg = EmailMultiAlternatives(subject,
                                     body_text,
                                     addr_from,
                                     addr_list,
                                     connection=connection,
                                     headers=headers)
        if html_message is not None:
            mimetype = "text/html"
            msg.attach_alternative(html_message, mimetype)
        for parts in attachments_parts:
            name = parts[0]
            msg.attach(name, parts[1])
        msg.send(fail_silently=fail_silently)


def send_mail_template(subject,
                       template,
                       addr_from,
                       recipient_list,
                       fail_silently=False,
                       attachments=None,
                       context=None,
                       connection=None,
                       headers=None):
    """
    Send email rendering text and html versions for the specified
    template name using the context dictionary passed in.
    """

    if context is None:
        context = {}

    # Loads a template passing in vars as context.
    def render(ext):
        name = "email_extras/%s.%s" % (template, ext)
        return loader.get_template(name).render(context)

    send_mail(subject,
              render("txt"),
              addr_from,
              recipient_list,
              fail_silently=fail_silently,
              attachments=attachments,
              html_message=render("html"),
              connection=connection,
              headers=headers)


def is_ajax(request: HttpRequest) -> bool:
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'