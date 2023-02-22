from django.http import HttpResponse

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from client.permissions import IsRoleAdmin
from client.activity_logs.filters import LogsFilter
from client.activity_logs.serializers import ActivityLogSerializer, ExportActivityLogSerializer
from client.models import ActivityLog
from mylib.queryset2excel import exportcsv


class ListActivityLogs(generics.ListAPIView):
    queryset = ActivityLog.objects.all().select_related("user")
    serializer_class = ActivityLogSerializer
    filter_class = LogsFilter
    permission_classes = [IsAuthenticated, IsRoleAdmin]


class ExportActivityLogs(generics.ListAPIView):
    queryset = ActivityLog.objects.all().select_related("user")
    serializer_class = ExportActivityLogSerializer
    filter_class = LogsFilter
    permission_classes = [IsAuthenticated, IsRoleAdmin]

    def list(self, request, *args, **kwargs):
        filename = "user_logs"
        fields = [s.name for s in self.get_queryset().model._meta.fields]
        headers = [{"name": "%s" % (k.replace("_", " ").title()), "value": k} for k in fields]
        queryset = self.get_serializer(self.get_queryset(), many=True).data
        path = exportcsv(
            filename=filename,
            queryset=queryset,
            headers=headers,
            title="User Logs",
            export_csv=True,
            request=self.request
        )

        try:
            with open(path, 'r') as f:
                file_data = f.read()

            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

        except IOError as e:
            print(e)
            response = Response({'detail': 'Error Occured'})

        return response
