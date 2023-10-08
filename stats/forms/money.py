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

class PaymentLinkSingleForm(forms.Form):
    description = forms.CharField(
        label="Описание",
        max_length=1000,
        required=False
    )
    email = forms.CharField(
        label="Email",
        max_length=100,
        required=False
    )
    status = forms.CharField(
        label="Статус",
        max_length=25,
        required=False
    )
