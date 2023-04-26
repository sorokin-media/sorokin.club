from django.forms import ModelForm
from users.models.affilate_models import AffilateInfo, AffilateLogs

class AffilateInfoForm(ModelForm):

    class Meta:
        model = AffilateInfo
        fields = [
            'fee_type',
        ]