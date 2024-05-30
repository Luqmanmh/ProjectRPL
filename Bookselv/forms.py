from django import forms

class fileupform(forms.Form):
    file = forms.FileField()