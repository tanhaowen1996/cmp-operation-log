from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import OperationLogSerializer
from .models import OperationLog
from .filters import OperationLogFilter


class OperationLogViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    list:
    Get alarm group list

    retrieve:
    Get alarm group detail with id

    """
    #authentication_classes = (OSAuthentication,)
    filterset_class = OperationLogFilter
    serializer_class = OperationLogSerializer
    queryset = OperationLog.objects.all()

    @action(detail=False, methods=['get'])
    def log_list(self):
        import pdb
        pdb.set_trace()
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(type_id=self.request.account_info['id'])
        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
