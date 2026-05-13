from typing import Any

from django.db.models import Count
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    DjangoModelPermissions
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet,
    ReadOnlyModelViewSet,
    ModelViewSet
)
from rest_framework.decorators import action

from debug_tools import QueryDebug
from my_app.models import Author
from my_app.permissions import IsStaffAndAdmin
from my_app.serializers import AuthorDetailSerializer, AuthorListSerializer


class AuthorsViewSet(ModelViewSet):
    queryset = Author.objects.prefetch_related('books')
    # permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    permission_classes = [DjangoModelPermissions, IsStaffAndAdmin]

    # serializer_class = AuthorListSerializer

    #    http method           viewset action
    #        get                  list
    #        get                  retrieve
    #        get                  get_statistic
    #        post                 create
    #        put                  update
    #        patch                partial_update
    #        delete               destroy

    def get_serializer_context(self) -> dict[str, Any]:
        context: dict[str, Any] = super().get_serializer_context()

        context['include-related'] = self.request.query_params.get(
            'include-related', 'false'
        ).lower() == 'true'  # True | False

        return context

    @QueryDebug(file_name="queries.log")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in {'list', 'get_statistic'}:
            return AuthorListSerializer
        return AuthorDetailSerializer

    @action(methods=['GET',], detail=False)
    def get_statistic(self, request: Request) -> Response:
        print("="*100)
        print(self.action)
        print("="*100)

        queryset = self.get_queryset().annotate(
            books_count=Count('books')
        )

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )


class AuthorListGenericView(ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorListSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        context: dict[str, Any] = super().get_serializer_context()

        context['include-related'] = self.request.query_params.get(
            'include-related', 'false'
        ).lower() == 'true'  # True | False

        return context


class AuthorRetrieveUpdateDestroyGenericView(RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorDetailSerializer

    lookup_field = 'username'  # поиск по колонке из БД
    lookup_url_kwarg = 'author'
