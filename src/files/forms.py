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
                                           'style': 'display: none;',
                                           'id': 'company_file'})
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
