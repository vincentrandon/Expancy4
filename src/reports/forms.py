import calendar

from django import forms

from reports.models import Report


class ReportForm(forms.ModelForm):
    """ Form to create a report. """

    date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date',
                                                                 'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}))

    class Meta:
        model = Report
        fields = ['title', ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-blue-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
        }
