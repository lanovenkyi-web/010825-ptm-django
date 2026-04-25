from my_app.serializers.book import BooksSerializer, BookCreateSerializer, BookUpdateSerializer
from my_app.serializers.category import CategoryNestedSerializer
from my_app.serializers.user import UserListSerializer, UserDetailSerializer, PromoteModeratorSerializer
from my_app.serializers.author import AuthorDetailSerializer, AuthorListSerializer

__all__ = [
    "BooksSerializer",
    "BookCreateSerializer",
    "BookUpdateSerializer",
    "CategoryNestedSerializer",
    "UserListSerializer",
    "UserDetailSerializer",
    "AuthorDetailSerializer",
    "AuthorListSerializer",
    "PromoteModeratorSerializer",
]
