import calendar

from django import forms

from reports.models import Report


class ReportForm(forms.ModelForm):
    """ Form to create a report. """

    date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Report
        fields = ['title', ]

