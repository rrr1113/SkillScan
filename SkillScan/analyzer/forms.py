from django.forms import ModelForm
from .models import Job

class EditJobForm(ModelForm):
    class Meta:
        model = Job
        exclude = ['created_by', "created_at", "updated_at", "company", "num_views"]
    def __init__(self, *args, **kwargs):
        super(EditJobForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'