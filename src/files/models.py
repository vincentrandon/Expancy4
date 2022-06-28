from django.db import models

# Create your models here.
from django.db.models import DO_NOTHING, JSONField
from django.utils.crypto import get_random_string

from accounts.models import Company, User, Transporter
from reports.models import Report


class CompanyFile(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True)
    header_row = models.IntegerField(default=0, null=True, blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, blank=True, null=True)
    data = JSONField(null=True, blank=True)
    slug = models.SlugField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(length=32)
        self.name = self.file.name
        super(CompanyFile, self).save(*args, **kwargs)


    class Meta:
        verbose_name = "Company File"
        verbose_name_plural = "Company Files"


class CompanyFileResult(models.Model):

    company_file = models.ForeignKey(CompanyFile, on_delete=models.CASCADE, blank=True, null=True)
    result_comparison_company = JSONField(null=True, blank=True)
    total_theorical_prices = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True) #Total




class TransporterFile(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    file = models.FileField(null=True, blank=False)
    transporter = models.ForeignKey(Transporter, on_delete=DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=DO_NOTHING, blank=True, null=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, blank=True, null=True)
    data = JSONField(null=True, blank=True)
    slug = models.SlugField(max_length=200, null=True, blank=True)


    def __str__(self):
        return str(self.transporter)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(length=32)
        self.name = self.file.name
        super(TransporterFile, self).save(*args, **kwargs)


class TransporterFileResults(models.Model):
    transporter_file = models.ForeignKey(TransporterFile, on_delete=models.CASCADE, blank=True, null=True)
    result_comparison_transporter = JSONField(null=True, blank=True)
    result_comparison_supplements = JSONField(null=True, blank=True)
    result_supplements = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    result_total_prices = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
