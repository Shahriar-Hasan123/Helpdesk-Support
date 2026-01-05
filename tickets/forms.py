from django import forms
from .models import Ticket, TicketComment


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["department", "subject", "description"]

class TicketUpdateManagerForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["status", "internal_notes", "assigned_agent"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_agent": forms.Select(attrs={"class": "form-select"}),
            "internal_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,        
                    "placeholder": "Internal notes (only visible to manager/agent)"
                }
            ),
        }

class TicketUpdateAgentForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["status"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ["message", "is_internal"]
