from django.db import models

# Create your models here.
from django.db.models import JSONField
from django.urls import reverse
from django.utils.crypto import get_random_string

from accounts.models import Company, Brand, Transporter


class Report(models.Model):

    """ Class designed to create a report and assign it to a company. """

    title = models.CharField(max_length=200, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True)

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('tool:single-report', kwargs={'slug': self.slug})


    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(length=32)
        super(Report, self).save(*args, **kwargs)

class ReportResults(models.Model):

    """ Class designed to create a report and assign it to a company. """

    report = models.ForeignKey(Report, on_delete=models.CASCADE, blank=True, null=True)
    transporter = models.ForeignKey(Transporter, on_delete=models.CASCADE, blank=True, null=True)
    result = JSONField(blank=True, null=True)
    result_comparison_weights = JSONField(blank=True, null=True)
    total_theorical_prices = models.FloatField(default=0, null=True, blank=True)
    total_calculated_prices = models.FloatField(default=0, null=True, blank=True)
    total_supplements = models.FloatField(default=0, null=True, blank=True)
    total_discrepancies = models.FloatField(default=0, null=True, blank=True)

    def __str__(self):
        return str(self.report)

