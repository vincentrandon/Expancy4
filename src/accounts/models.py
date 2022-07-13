from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db import models

# Create your models here.
from django.db.models import DO_NOTHING
from django.utils.safestring import mark_safe


class User(AbstractBaseUser, PermissionsMixin):

    """ Class designed to create users. """

    username = models.CharField('username', max_length=30, blank=True)
    email = models.EmailField('Adresse mail', unique=True)
    first_name = models.CharField('Prénom', max_length=30, blank=True)
    last_name = models.CharField('Nom', max_length=30, blank=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    company = models.ForeignKey('Company', on_delete=DO_NOTHING, blank=True, null=True)
    brand = models.ForeignKey('Brand', on_delete=DO_NOTHING, blank=True, null=True)
    avatar = models.FileField('Avatar', blank=True)
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff status', default=False)
    is_superuser = models.BooleanField(default=False)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'



    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


################################
# Classe dédiée aux transporteurs
################################

class Transporter(models.Model):

    """ Class designed to create a transporter. """

    name = models.CharField(max_length=100)
    avatar = models.ImageField(blank=True, null=True)
    avatar_file_to_upload = models.ImageField(blank=True, null=True)
    avatar_file_uploaded = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name

    def image_tag(self):
        if self.avatar:
            return mark_safe('<img src="%s" style="width: 150px; height:150px;" />' % self.avatar.url)
        else:
            return 'No Image Found'

    image_tag.short_description = 'Image'

    class Meta:
        verbose_name_plural = "transporters"


########################################
# Classe dédiée aux clients (entreprises)
########################################

class Company(models.Model):

    """ Class designed to create a company. """

    name = models.CharField(max_length=200, blank=False)
    transporters = models.ManyToManyField(Transporter, blank=True)

    # employees = User.objects.filter(company=company)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"


class Brand(models.Model):
    name = models.CharField(max_length=100, blank=False)
    company = models.ForeignKey(Company, on_delete=DO_NOTHING, blank=False, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class CompanyDetailsIntegration(models.Model):
    company = models.ForeignKey(Company, on_delete=DO_NOTHING, blank=False, null=True)
    brand = models.ForeignKey(Brand, on_delete=DO_NOTHING, blank=True, null=True)
    transporter = models.ForeignKey(Transporter, on_delete=DO_NOTHING, blank=True, null=True)
    header_row = models.CharField(max_length=100, blank=True, null=True)
    column_weight = models.JSONField(blank=True, null=True)
    column_package_number = models.JSONField(blank=True, null=True)
    column_date = models.JSONField(blank=True, null=True)
    slug = models.SlugField(max_length=200, blank=True, null=True)


    #Titre de la page
    def __str__(self):
        if self.brand:
            return "[" + str(self.company) + " - " + str(self.brand) + "] " + str(self.transporter)
        else:
            return "[" + str(self.company) + "] " + str(self.transporter)