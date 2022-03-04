from django_filters import (
    FilterSet,
    CharFilter,
    DateFilter,)
from .models import OperationLog


class OperationLogFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    server_name = CharFilter(field_name='server_name', lookup_expr='icontains')
    server_id = CharFilter(field_name='server_id', lookup_expr='icontains')
    volume_id = CharFilter(field_name='volume_id', lookup_expr='icontains')
    volume_name = CharFilter(field_name='volume_name', lookup_expr='icontains')
    created_at = DateFilter(field_name='created_at__date', lookup_expr='contains')

    class Meta:
        mode = OperationLog
        filter = ('name', 'user_name', 'server_name', 'server_id', 'volume_id', 'volume_name', 'created_at')
