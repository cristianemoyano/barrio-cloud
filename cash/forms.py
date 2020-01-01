from django import forms


class RevertEntryForm(forms.Form):
    pk = forms.IntegerField(label='Entry Pk')
