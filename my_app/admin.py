from django.contrib import admin, messages
from django.contrib.admin import action
from django.db.models import QuerySet, F

from my_app.models import Book, Author, AuthorProfile, Post


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "price",
        "category",
        "published_date",
        "custom_method"
    ]

    search_fields = [
        "title",
    ]

    list_filter = [
        "published_date",
        "category"
    ]

    list_editable = [
        "category",
        "price"
    ]

    list_per_page = 25

    actions = ["custom_action"]

    @admin.display(description="Custom Field")
    def custom_method(self, obj: Book):
        return "NEW FIELD"

    @admin.action(description="Увеличение цены на + 10%%")
    def custom_action(self, request, queryset: QuerySet):
        queryset.update(price=F('price') * 1.1)

        self.message_user(
            request,
            f"Цены для {queryset.count()} книг успешно увеличены на 10%",
            messages.SUCCESS
        )


class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    extra = 1


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        'username',
        'first_name',
        'last_name',
        'count_of_posts',
    ]

    search_fields = [
        'username',
        'last_name'
    ]

    inlines = [
        AuthorProfileInline
    ]


    @admin.display(description="count of posts")
    def count_of_posts(self, obj: Author):
        return obj.posts.count()


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    ...


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    ...
