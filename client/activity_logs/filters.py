import django_filters
from django.db.models import Q
from django_filters.rest_framework import FilterSet

from client.models import ActivityLog


class LogsFilter(FilterSet):
    search = django_filters.CharFilter(label="Search", method="filter_name")

    class Meta:
        model = ActivityLog
        fields = ("__all__")

    def filter_name(self, queryset, name, value):
        return queryset.filter(Q(user__username__icontains=value) | Q(user__first_name__icontains=value) | Q(user__last_name__icontains=value))
