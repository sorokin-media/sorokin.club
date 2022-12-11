from django import forms


class DateForm(forms.Form):
    date_from = forms.DateField(
        label="Дата С (формат 2022-12-31)",
        required=True,
    )
    date_to = forms.DateField(
        label="Дата По (формат 2022-12-01)",
        required=True,
    )
