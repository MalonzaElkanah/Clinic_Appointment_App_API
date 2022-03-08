from django.urls import path

from client.activity_logs.views import ListActivityLogs, ExportActivityLogs

urlpatterns=[
	path('', ListActivityLogs.as_view(), name="activity_log_list"),
	path('export/', ExportActivityLogs.as_view(), name="activity_log_export"),
]