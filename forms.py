from django import forms
from .models import Project, ProjectImage

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'content', 'thumbnail', 'category', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption']

ProjectImageFormSet = forms.inlineformset_factory(
    Project, ProjectImage, form=ProjectImageForm,
    extra=3, can_delete=True, max_num=10
)

