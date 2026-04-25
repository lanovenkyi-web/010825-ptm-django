from urllib.request import Request

from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from my_app.models import User
from my_app.permissions import IsAdminOnly, CreateActionPermanentBlocked
from my_app.serializers import UserListSerializer, UserDetailSerializer, PromoteModeratorSerializer
from my_app.serializers.user import UserLoginSerializer, RegisterUserSerializer
from my_app.utils import set_jwt_cookies, REFRESH_COOKIE_NAME, clear_jwt_cookies



class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOnly, CreateActionPermanentBlocked]

    def get_serializer_class(self):
        if self.action == 'promote_to_moderator':
            return PromoteModeratorSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserDetailSerializer

    @action(detail=True, methods=['patch'], url_path='promote-to-moderator')
    def promote_to_moderator(self, request: Request, *args, **kwargs) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(
            status=status.HTTP_200_OK
        )



class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, *args, **kwargs) -> Response:
        data = request.data

        serializer = UserLoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        try:
            response = Response(
                status=status.HTTP_200_OK,
            )

            set_jwt_cookies(response=response, user=user)

            # 6. вернуть ответ
            return response

        except Exception as e:
            # 6. вернуть ответ
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={
                    "message": str(e)
                }
            )


class LogoutUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            refresh_token = request.COOKIES.get(REFRESH_COOKIE_NAME)

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

        except TokenError:
            pass

        except Exception as e:
            return Response(
                data={
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response = Response(
            status=status.HTTP_200_OK,
        )

        clear_jwt_cookies(response=response)

        return response


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

        return response


# class UserListGenericView(GenericAPIView):
#     def get(self, request: Request) -> Response:
#         qs = User.objects.all()
#
#         serializer = UserListSerializer(qs, many=True)
#
#         return Response(
#             data=serializer.data,
#             status=status.HTTP_200_OK
#         )

# class UserListCreateGenericView(GenericAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserListSerializer
#
#     def get(self, request: Request) -> Response:
#         qs = self.get_queryset()
#
#         serializer = self.get_serializer(qs, many=True)
#
#         return Response(
#             data=serializer.data,
#             status=status.HTTP_200_OK
#         )
#
#     def post(self, request: Request) -> Response:
#         serializer = self.get_serializer(data=request.data)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 data=serializer.data,
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(
#             data=serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )


# class UserListCreateGenericView(GenericAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserListSerializer
#
#     def get(self, request: Request) -> Response:
#         qs = self.get_queryset()
#
#         serializer = self.get_serializer(qs, many=True)
#
#         return Response(
#             data=serializer.data,
#             status=status.HTTP_200_OK
#         )
#
#     def post(self, request: Request) -> Response:
#         serializer = self.get_serializer(data=request.data)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 data=serializer.data,
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(
#             data=serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )


class UserListCreateGenericView(ListCreateAPIView):
    queryset = User.objects.filter(deleted=False)
    serializer_class = UserListSerializer

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.get_queryset().annotate(
            books_count=Count('published_books')
        )

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            data={
                "total_objects": self.get_queryset().count(),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def create(self, request: Request, *args, **kwargs) -> Response:
        data = request.data.copy()

        if 'first_name' not in data:
            data['first_name'] = 'Unknown'

        if 'last_name' not in data:
            data['last_name'] = 'Unknown'

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserRetrieveUpdateDestroyGenericView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
