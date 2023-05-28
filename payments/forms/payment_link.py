from django import forms
from payments.models import PaymentLink


class PaymentLinkForm(forms.Form):
    title = forms.CharField(
        label="Заголовок",
        max_length=256,
        required=True
    )

    description = forms.CharField(
        label="Описание",
        max_length=1000,
        required=True
    )

    amount = forms.IntegerField(
        label="Сумма",
        initial=3999,
        required=True
    )
