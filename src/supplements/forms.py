from django import forms

from supplements.models import Supplement


class SupplementForm(forms.ModelForm):

    class Meta:

        model = Supplement
        exclude = ['transporter', 'company', 'slug', 'brand',]