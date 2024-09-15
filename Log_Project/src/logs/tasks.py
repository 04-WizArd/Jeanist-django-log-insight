# from celery import shared_task
# from .models import LogFile, LogEntry, LogSummary
# import re
# from datetime import datetime

# @shared_task
# def analyze_log_file(log_file_id):
#     log_file = LogFile.objects.get(id=log_file_id)
    
#     with open(log_file.path, 'r') as file:
#         lines = file.readlines()
    
#     pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)'
    
#     entries = []
#     for line in lines:
#         match = re.match(pattern, line)
#         if match:
#             timestamp, level, message = match.groups()
#             entries.append(LogEntry(
#                 log_file=log_file,
#                 timestamp=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
#                 level=level,
#                 message=message
#             ))
    
#     LogEntry.objects.bulk_create(entries)
    
#     # Create summary
#     summary = LogSummary(
#         log_file=log_file,
#         date=datetime.now().date(),
#         error_count=sum(1 for e in entries if e.level == 'ERROR'),
#         warning_count=sum(1 for e in entries if e.level == 'WARNING'),
#         info_count=sum(1 for e in entries if e.level == 'INFO'),
#     )
#     summary.save()
    
#     log_file.last_analyzed = datetime.now()
#     log_file.save()


from celery import shared_task
from .models import LogFile, LogEntry, LogSummary
import re
from datetime import datetime
from django.db.models import Count
from django.utils import timezone

@shared_task
def analyze_log_file(log_file_id):
    log_file = LogFile.objects.get(id=log_file_id)
    
    with log_file.file.open('r') as file:
        lines = file.readlines()
    
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (\w+) - (.+)'
    
    entries = []
    for line in lines:
        match = re.match(pattern, line)
        if match:
            timestamp, level, source, message = match.groups()
            entries.append(LogEntry(
                log_file=log_file,
                timestamp=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                level=level,
                source=source,
                message=message
            ))
    
    # Bulk create entries in chunks to avoid memory issues
    chunk_size = 1000
    for i in range(0, len(entries), chunk_size):
        LogEntry.objects.bulk_create(entries[i:i+chunk_size])
    
    # Create summary
    summary_date = timezone.now().date()
    summary, created = LogSummary.objects.get_or_create(
        log_file=log_file,
        date=summary_date
    )
    
    # Update summary counts
    level_counts = LogEntry.objects.filter(log_file=log_file, timestamp__date=summary_date).values('level').annotate(count=Count('id'))
    
    summary.total_entries = sum(item['count'] for item in level_counts)
    for item in level_counts:
        setattr(summary, f"{item['level'].lower()}_count", item['count'])
    
    # Calculate average response time (assuming it's available in the log)
    # This is a placeholder and should be adjusted based on your actual log format
    response_times = LogEntry.objects.filter(log_file=log_file, timestamp__date=summary_date, message__contains="response_time:")
    if response_times.exists():
        avg_response_time = response_times.average('response_time')
        summary.avg_response_time = avg_response_time
    
    summary.save()
    
    log_file.last_analyzed = timezone.now()
    log_file.save()

    return f"Analyzed {summary.total_entries} entries for {log_file.name}"