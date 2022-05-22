""" Model for payment app"""
from django.db import models
from django.conf import settings
import datetime
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from common import library as custom_lib
from .constants import USER_TYPE_CHOICES, USER_TYPE_CUSTOMER
# Create your models here.


class Client(DjangoAbstractUser):
    """
    User model.

    Attribs:
        user (obj): Django user model.
        dob(datetime): date of birth of user.
        phone (str): phone number of the user
        address(str): address of the user.
        image (img): user image.
        blocked(bool): field which shows the active status of user.
        terms_accepted(bool): boolean value indicating whether the
            terms are accepted by the user.

    """
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(
        default='', max_length=200, blank=True)
    address = models.CharField(
        default='', max_length=2000, blank=True)
    image = models.ImageField(
        upload_to=custom_lib._get_file_path,
        null=True, default=None, blank=True)
    type = models.IntegerField(
        default=USER_TYPE_CUSTOMER, choices=USER_TYPE_CHOICES)
    terms_accepted = models.BooleanField(default=False)
    privacy_accepted = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    blocked = models.BooleanField(default=False)
    updated_email = models.EmailField(null=True, blank=True,
                                      default='')

    def __str__(self):
        """Object name in django admin."""
        return '%s : %s' % (self.name, self.id)

    def save(self, *args, **kwargs):
        if 'email' in kwargs:
            kwargs['username'] = kwargs['email']
        super(Client, self).save(*args, **kwargs)

    @property
    def idencode(self):
        """To return encoded id."""
        return custom_lib._encode(self.id)

    @property
    def name(self):
        """Get user full name."""
        return '%s' % (self.get_full_name())

    def issue_access_token(self, device=None):
        """Function to get or create user access token."""
        old_tokens = AccessToken.objects.filter(user=self)
        if old_tokens.count() > 1:
            old_tokens.exclude(id=old_tokens.first().id).delete()
        token, created = AccessToken.objects.get_or_create(user=self)
        if device:
            device.activate()
        self.last_login = timezone.now()
        self.save()
        return token.key


class AccessToken(models.Model):
    """
    The default authorization token model.

    This model is overriding the DRF token
    Attribs:
        user(obj): user object
        Key(str): token
        created(datetime): created date and time.
    """

    user = models.ForeignKey(
        Client, related_name='auth_token',
        on_delete=models.CASCADE)
    key = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Function to return value in django admin."""
        return self.key

    def save(self, *args, **kwargs):
        """Overriding the save method to generate key."""
        if not self.key:
            self.key = self.generate_unique_key()
        return super(AccessToken, self).save(*args, **kwargs)

    def generate_unique_key(self):
        """Function to generate unique key."""
        key = get_random_string(settings.ACCESS_TOKEN_LENGTH)
        if AccessToken.objects.filter(key=key).exists():
            self.generate_unique_key()
        return key

    def refresh(self):
        """Function  to change token."""
        self.key = self.generate_unique_key()
        self.save()
        return self.key


class Project(models.Model):
    """
       project model.

       Attribs:
           name (str): Name of the project
           client(obj): client object.

    """
    name = models.CharField(
        max_length=100, default='', null=True, blank=True)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='project_clients')

    def __str__(self):
        return '%s : %s' % (self.name, self.id)

    @property
    def idencode(self):
        """To return encoded id."""
        return custom_lib._encode(self.id)


class Invoice(models.Model):
    """
       Invoice model.

       Attribs:
           project (obj): project object.
           invoice_number(str): number of invoice.
           invoice_date (str): date of invoice.
           amount(int): amount in invoice
           note (str): note for invoice.
           stripe_payment_link(str): link for payment.

    """

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='project_invoice')
    invoice_number = models.CharField(
        max_length=100, default='', blank=True)
    invoice_date = models.DateTimeField(default=datetime.datetime.today)
    amount = models.IntegerField(default=0)
    note = models.CharField(max_length=1000, default='', blank=True)
    stripe_payment_link = models.CharField(
        max_length=200, default='', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s : %s' % (self.project.name, self.invoice_number)

    @property
    def idencode(self):
        """To return encoded id."""
        return custom_lib._encode(self.id)

