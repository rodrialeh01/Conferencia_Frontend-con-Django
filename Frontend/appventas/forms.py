from django import forms


class FileForm(forms.Form):
    file = forms.FileField(label='file')

class InputTextAreaForm(forms.Form):
    entrada = forms.CharField(label='entrada')