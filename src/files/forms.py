from django import forms

from files.models import TransporterFile, CompanyFile


class TransporterFileForm(forms.ModelForm):
    transporter_form = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = TransporterFile
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={'onchange': 'submit();', 'style': 'display: none;', 'id': 'transporter_file'}),
        }


class CompanyFileForm(forms.ModelForm):
    company_form = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = CompanyFile
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={'onchange': 'submit();',
                                           'class': 'ml-5 bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'}),
        }


class DeleteCompanyFileForm(forms.ModelForm):
    delete_company_file = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = CompanyFile
        fields = []


class DeleteTransporterFileForm(forms.ModelForm):
    delete_transporter_file = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = CompanyFile
        fields = []
