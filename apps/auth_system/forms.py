from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    account_type = forms.ChoiceField(
        choices=[
            ('customer', 'Customer - Marketplace Access'),
            ('staff_request', 'Request Staff Access - Requires Approval')
        ],
        required=True,
        help_text='Staff access requires approval from authorized team members'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'account_type')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['account_type'].widget.attrs.update({'class': 'form-select'})