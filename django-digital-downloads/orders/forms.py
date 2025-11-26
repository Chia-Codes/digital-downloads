from django import forms

from .models import UserNote


# Form for creating and updating user notes
class UserNoteForm(forms.ModelForm):
    class Meta:
        model = UserNote
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "maxlength": 120}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
        }

    # Validate title and body lengths
    def clean_title(self):
        title = (self.cleaned_data.get("title") or "").strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title

    def clean_body(self):
        body = (self.cleaned_data.get("body") or "").strip()
        if len(body) < 5:
            raise forms.ValidationError("Body must be at least 5 characters.")
        return body
