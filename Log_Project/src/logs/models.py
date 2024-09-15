# from django.db import models

# class LogFile(models.Model):
#     name = models.CharField(max_length=255)
#     path = models.CharField(max_length=1000)
#     last_analyzed = models.DateTimeField(null=True, blank=True)

# class LogEntry(models.Model):
#     log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField()
#     level = models.CharField(max_length=20)  # ERROR, WARNING, INFO, etc.
#     message = models.TextField()
    
# class LogSummary(models.Model):
#     log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE)
#     date = models.DateField()
#     error_count = models.IntegerField(default=0)
#     warning_count = models.IntegerField(default=0)
#     info_count = models.IntegerField(default=0)
#     avg_response_time = models.FloatField(null=True)



from django.db import models
from django.contrib.auth.models import User

class LogFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='logs/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_analyzed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class LogEntry(models.Model):
    LOG_LEVELS = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE, related_name='entries')
    timestamp = models.DateTimeField()
    level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    source = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.timestamp} - {self.level}: {self.message[:50]}..."

class LogSummary(models.Model):
    log_file = models.ForeignKey(LogFile, on_delete=models.CASCADE, related_name='summaries')
    date = models.DateField()
    total_entries = models.IntegerField(default=0)
    debug_count = models.IntegerField(default=0)
    info_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    critical_count = models.IntegerField(default=0)
    avg_response_time = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Summary for {self.log_file.name} on {self.date}"

    class Meta:
        unique_together = ('log_file', 'date')