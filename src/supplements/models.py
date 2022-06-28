from django.db import models

# Create your models here.
from django.db.models import DO_NOTHING, JSONField
from django.template.defaultfilters import slugify
from django.urls import reverse

from accounts.models import Transporter, Company, Brand


class Supplement(models.Model):

    """ Class designed to implement a "Supplement" for a company and a transporter.
    Supplements (extra-fees) are necessary to recalculate deliveries. """


    transporter = models.ForeignKey(Transporter, on_delete=DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=DO_NOTHING, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=DO_NOTHING, blank=True, null=True)
    supplements = JSONField(null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)


    #Titre de la page
    def __str__(self):
        if self.brand:
            return "[" + str(self.company) + " - " + str(self.brand) + "] " + str(self.transporter)
        else:
            return "[" + str(self.company) + "] " + str(self.transporter)

    #URL du supplément créé
    def get_absolute_url(self):
        return reverse("transporter-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.brand:
                self.slug = slugify(
                    str("tarifs-") + str(self.company) + "-" + str(self.brand) + "-" + str(self.transporter))
            else:
                self.slug = slugify(str("tarifs-") + str(self.company) + "-" + str(self.transporter))

        elif 'none' in self.slug:
            if self.brand:
                self.slug = slugify(
                    str("tarifs-") + str(self.company) + "-" + str(self.brand) + "-" + str(self.transporter))
            else:
                self.slug = slugify(str("tarifs-") + str(self.company) + "-" + str(self.transporter))


        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Supplément"
        verbose_name_plural = "Suppléments"


class TransporterImplementation(models.Model):

    """ Class designed to complete the "Supplement" class.
     This class is used to select variables in order to proceed to the comparison. """

    supplement = models.ForeignKey(Supplement, on_delete=models.CASCADE, blank=False)
    header_row = models.IntegerField(blank=True, null=True)
    columns_to_keep = JSONField(blank=True, null=True)
    column_price = JSONField(blank=True, null=True)
    column_package_number = JSONField(blank=True, null=True)
    column_prestation_type = JSONField(blank=True, null=True)
    column_weight = JSONField(blank=True, null=True)
    columns_supplements = JSONField(blank=True, null=True)
    column_date = JSONField(blank=True, null=True)



    class Meta:
        verbose_name = "Supplément - Detail per company"
        verbose_name_plural = "Suppléments - Details per company"


class Weight(models.Model):

    """ Class designed to store weights per company AND transporter. """

    transporter = models.ForeignKey(Transporter, on_delete=DO_NOTHING, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=DO_NOTHING, blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=DO_NOTHING, blank=True, null=True)
    columns_to_keep = JSONField(blank=True, null=True)



    def __str__(self):
        if self.brand:
            return "Poids [" + str(self.company) + " - " + str(self.brand) + "] " + str(self.transporter)
        else:
            return "Poids [" + str(self.company) + "] " + str(self.transporter)


    class Meta:
        verbose_name = "Weight"
        verbose_name_plural = "Weights"

class WeightPrices(models.Model):

    """ Class designed to store list of weights and their prices. """

    weight = models.ForeignKey(Weight, on_delete=DO_NOTHING, blank=False, null=True)
    min_weight = models.FloatField('Min weight', blank=False, null=True)
    max_weight = models.FloatField('Max weight', blank=False, null=True)
    price = models.FloatField('Price', blank=False, null=True)

    class Meta:
        verbose_name = "Weight Price"
        verbose_name_plural = "Weight Prices"

