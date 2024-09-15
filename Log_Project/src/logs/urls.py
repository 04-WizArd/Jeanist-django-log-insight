from django.urls import path
from logs.views import UploadLogFileView, AnalysisResultsView, IndexView
from .views import RegisterView

app_name = 'logs'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('upload/', UploadLogFileView.as_view(), name='upload_log'),
    path('results/<int:log_file_id>/', AnalysisResultsView.as_view(), name='analysis_results'),
]