from django import forms
from .models import LogEntry, LogFile

class LogFileUploadForm(forms.ModelForm):
    class Meta:
        model = LogFile
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
            'file': forms.FileInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}),
        }

class LogFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-md'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-md'}))
    log_level = forms.ChoiceField(choices=[('', 'All')] + LogEntry.LOG_LEVELS, required=False, widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-md'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-md', 'placeholder': 'Search logs...'}))