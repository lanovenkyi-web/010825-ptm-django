from datetime import datetime
from decimal import Decimal

from django.contrib.auth.base_user import AbstractBaseUser
# from django.contrib.auth.models import User
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.core.validators import MinLengthValidator


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        admin = "admin", "Admin"
        moderator = "moderator", "Moderator"
        lib_member = "lib_member", "Library Member"

    class Gender(models.TextChoices):
        male = "male", "Male"
        female = "female", "Female"
        other = "other", "Other"

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=80, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=15, choices=Role)
    gender = models.CharField(max_length=10, choices=Gender)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "role", "gender"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "users"


class Book(models.Model):  # table name like <app_name>_<model_name>
    CATEGORY_CHOICES = [
        ('Fantasy', 'FANTASY CATEGORY'),
        ('Mystic', 'MYSTIC CATEGORY'),
        ('Biography', 'BIOGRAPHY CATEGORY'),
        ('N/A', 'UNRECOGNISED CATEGORY'),
    ]

    title: str = models.CharField(
        max_length=125,
        unique=True,
        verbose_name="Название книги",
        error_messages={  #  пересмотреть настройку параметра
            'blank': 'Сожалеем, но книгу нельзя создать без названия книги.',
            'unique': 'Кажется книга с таким названием уже существует.',
        }
    )
    description: str = models.TextField(
        verbose_name="Описание книги",
        validators=[
            MinLengthValidator(20),
            # MaxLengthValidator(500)
        ]
    )
    comment: str = models.TextField(
        null=True,
        blank=True,
        # unique_for_date='published_date'
        # unique_for_month='published_date'
        # unique_for_year='published_date'
    )
    published_date: datetime = models.DateTimeField(verbose_name="Дата публикации")
    price: Decimal = models.DecimalField(  # 123.45
        verbose_name="Цена книги",
        help_text="Цена книги в евро. Должно быть больше 0",
        max_digits=5,
        decimal_places=2,
        null=True,  #  сторона базы данных
        blank=True  #  сторона админ панели
    )
    category: str = models.CharField(
        verbose_name="Категория книги",
        help_text="Категория книги из списка предложенных. Если неизвестна, выберите 'N/A'",
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='N/A',
        # editable=False
    )
    # isbn: str = models.SlugField()

    def __str__(self):
        # return self.title
        return f"{self.title} ({self.published_date})   --- {self.id}"

    # def __str__(self):
    #     return str(self)


    class Meta:
        db_table = "books"  # своё имя таблицы в БД

        verbose_name = "Book"  # человекочитабельное название класса (ед. число)
        verbose_name_plural = "Books"  # человекочитабельное название класса (множ. число)
        ordering = ["-published_date", "title"]  # desc
        # ordering = ["published_date",]  # asc

        indexes = [
            models.Index(
                fields=["title", "category"],
                name="book_title_category_idx"
            )
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["title", "category"],
                name="book_title_category_unq_cst"
            )
        ]

        # abstract = True
        # default_related_name = "books"

        get_latest_by = "-published_date"


class Post(models.Model):
    title: str = models.CharField(
        max_length=200
    )
    content: str = models.TextField(
        validators=[
            MinLengthValidator(50)
        ]
    )

    # One to Many RelationShip
    author = models.ForeignKey(
        'Author',
        # on_delete=models.DO_NOTHING,  # при удалении родителя ничего не делай
        # on_delete=models.CASCADE,  # при удалении родителя удаляй все связанные записи КАСКАДНО
        on_delete=models.SET_NULL,  # обязательно требует включение null=True. При удалении родителя устанавливай значение NULL для всех его дочерних объектов
        # on_delete=models.SET_DEFAULT,  # обязательно требует включение default=<default value>. При удалении родителя устанавливай значение по умолчанию для всех его дочерних объектов
        # on_delete=models.PROTECT  # запретить удаление родителя, пока на него есть ХОТЬ ОДНА ССЫЛКА
        null=True,
        blank=True,
        related_name='posts'
    )

    created_at: datetime = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        author = self.author.username if self.author else "Unknown author"

        return f"{self.title} Publisher: ({author})"

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]


# Post.author -> -> Author obj.
# Author.posts -> ->  [Post obj, ... Post obj]

class Author(models.Model):
    username: str = models.CharField(
        max_length=30,
        unique=True
    )
    first_name: str = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    last_name: str = models.CharField(
        max_length=25,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = "authors"
        ordering = ["username",]


class AuthorProfile(models.Model):
    about: str = models.TextField(
        null=True
    )
    personal_website: str = models.URLField(
        max_length=255,
        null=True,
        blank=True
    )
    avatar: str = models.ImageField(
        upload_to='avatars/'
    )

    author = models.OneToOneField(
        Author,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    def __str__(self):
        # Сперва система получает все данные (SELECT * FROM '<AuthorProfile>')

        # При обращении к author.username, система пойдёт на +1 запрос (SELECT * FROM '<Author> WHERE id = <%s>')
        return self.author.username

    class Meta:
        db_table = "author_profiles"
