# from django.shortcuts import render, redirect
# from django.views import View
# from .models import LogFile, LogEntry, LogSummary
# from .forms import LogFileUploadForm
# from .tasks import analyze_log_file
# import os

# class UploadLogFileView(View):
#     def get(self, request):
#         form = LogFileUploadForm()
#         return render(request, 'log_analysis/upload.html', {'form': form})
    
#     def post(self, request):
#         form = LogFileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             log_file = form.save()
#             analyze_log_file.delay(log_file.id)
#             return redirect('analysis_results', log_file_id=log_file.id)
#         return render(request, 'log_analysis/upload.html', {'form': form})

# class AnalysisResultsView(View):
#     def get(self, request, log_file_id):
#         log_file = LogFile.objects.get(id=log_file_id)
#         summary = LogSummary.objects.filter(log_file=log_file).order_by('-date')
#         entries = LogEntry.objects.filter(log_file=log_file).order_by('-timestamp')[:100]
#         return render(request, 'log_analysis/results.html', {
#             'log_file': log_file,
#             'summary': summary,
#             'entries': entries
#         })

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views import View
from django.core.paginator import Paginator
from .models import LogFile, LogEntry, LogSummary
from .forms import LogFileUploadForm, LogFilterForm
from .tasks import analyze_log_file

class IndexView(View):
    def get(self, request):
        # Récupérer tous les fichiers de log, triés par date de téléchargement (du plus récent au plus ancien)
        log_files = LogFile.objects.all().order_by('-uploaded_at')

        # Pagination
        paginator = Paginator(log_files, 10)  # Afficher 10 fichiers par page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Formulaire de téléchargement pour un accès rapide
        upload_form = LogFileUploadForm()

        context = {
            'log_files': page_obj,
            'upload_form': upload_form,
        }
        return render(request, 'logs/index.html', context)
    
class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'auth/register.html'

class UploadLogFileView(View):
    def get(self, request):
        form = LogFileUploadForm()
        return render(request, 'logs/upload.html', {'form': form})
    
    def post(self, request):
        form = LogFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            log_file = form.save(commit=False)
            log_file.uploaded_by = request.user
            log_file.save()
            analyze_log_file.delay(log_file.id)
            return redirect('analysis_results', log_file_id=log_file.id)
        return render(request, 'logs/upload.html', {'form': form})

class AnalysisResultsView(View):
    def get(self, request, log_file_id):
        log_file = LogFile.objects.get(id=log_file_id)
        summaries = LogSummary.objects.filter(log_file=log_file).order_by('-date')
        
        filter_form = LogFilterForm(request.GET)
        entries = LogEntry.objects.filter(log_file=log_file).order_by('-timestamp')
        
        if filter_form.is_valid():
            start_date = filter_form.cleaned_data.get('start_date')
            end_date = filter_form.cleaned_data.get('end_date')
            log_level = filter_form.cleaned_data.get('log_level')
            search = filter_form.cleaned_data.get('search')
            
            if start_date:
                entries = entries.filter(timestamp__date__gte=start_date)
            if end_date:
                entries = entries.filter(timestamp__date__lte=end_date)
            if log_level:
                entries = entries.filter(level=log_level)
            if search:
                entries = entries.filter(message__icontains=search)
        
        paginator = Paginator(entries, 50)  # Show 50 entries per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'log_file': log_file,
            'summaries': summaries,
            'entries': page_obj,
            'filter_form': filter_form,
        }
        return render(request, 'logs/results.html', context)