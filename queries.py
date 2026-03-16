import os
from datetime import datetime
from decimal import Decimal
from pprint import pformat

import django
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()

# ВСЕ, вообще ВСЕ импорты НАШИХ локальных файлов -- строго после django.setup()

from django.db.models import Q, F

from my_app.models import Book



# Получение списка всех книг
# all_books = Book.objects.all()
#
# print(all_books.query)
# print(all_books)
# print(type(all_books))



# Создение объектов

# Вариант 1 (быстрый)
# new_book = Book.objects.create(
#     title="TEST TITLE FROM ORM CREATION",
#     description="QWERTYQWERTYQWERTYQWERTYQWERTYQWERTYQWERTYQWERTYQWERTY",
#     published_date="2026-03-06 14:23:41"
# )
#
# print("Book was created")
#
# print(new_book)


# Вариант 2 (с возможностью промежуточной работы)

# new_book = Book(
#     title="NEW BOOK WITH SAVE METHOD",
#     description="QWERTYQWERTYQWERTYQWERTY22222222222222222222222222",
#     published_date="2026-03-06 14:30:41",
#     price=Decimal("7.33")
# )
#
# new_book.category = "Biography"
# new_book.save()



# books = Book.objects.all()  # -> -> <QuerySet[obj1, obj2, ..., obj282]>
#
# print(books.query)  # помогает смотреть сырой SQL запрос
#
# for book in books:
#     print(book.title, book.published_date)


# first_book = Book.objects.all().first()
#
# print(first_book)
# print(type(first_book))
#
# print(first_book.title, first_book.published_date, first_book.id)


# last_book = Book.objects.all().last()
#
# print(last_book)
# print(type(last_book))
#
# print(last_book.title, last_book.published_date, last_book.id)



# count_of_books = Book.objects.all().count()
# print(f"Общее кол.во книг в базе данных = {count_of_books}")


# count_of_books = Book.objects.all()
#
# if not count_of_books.exists():
#     print("По вашему запросу ничего не найдено")
# else:
#     print(f"Данные получены, есть {count_of_books.count()} объектов")





# Получение одного объекта

# try:
#     book = Book.objects.get(id=281)
#
#     print(book)
# except Book.MultipleObjectsReturned:
#     print("По категории вернулось более одного объекта")
#
# except Book.DoesNotExist:
#     print("По категории ничего не найдено")



# books = Book.objects.filter(
#     # title__exact="A Game of Thrones"  # полное совпадение
#     # title__exact="a game of thrones"  # контент сопадает, но разный регистр
#     title__iexact="a game of thrones"  # i -- ignore case sensitive
# )

# books = Book.objects.filter(
#     title__contains="harry potter and"
# )
#
# print(books.query)
#
# print(books.count())



# books = Book.objects.filter(
#     category__in=["Mystic", "N/A"]
# )
#
# print(books.query)
# print(books.count())



# books = Book.objects.filter(
#     id__in=[1, 3, 5, 7, 9]
# )
#
# print(books.query)
# print(books.count())



# # получить книги, цена которых больше 7
# books = Book.objects.filter(
#     price__gt=20
# )
#
# print(books.query)
# print(books.count())



# получить книги, где нет комментариев
# books = Book.objects.filter(
#     comment__isnull=True
# )
#
# print(books.query)
# print(books.count())


# получить книги, где есть коммент
# books = Book.objects.filter(
#     comment__isnull=False
# )
#
# print(books.query)
# print(books.count())



# books = Book.objects.filter(
#     description__startswith="Epic"
# )
#
# print(books.query)
# print(books.count())
#
# for obj in books:
#     print(obj.description)



# books = Book.objects.filter(
#     title__endswith="Dune"
# )
#
# print(books.query)
# print(books.count())
#
# for obj in books:
#     print(obj.title)



# получить книги с ценой от 14 до 18
# books = Book.objects.filter(
#     price__range=[14, 18]
# )
#
# print(books.query)
# print(books.count())
#
# for obj in books:
#     print(obj.price)



# получить все книги с 2023 по 2026 года
# books = Book.objects.filter(
#     published_date__range=["2023-01-01", datetime.now()]
# )
#
# print(books.query)
# print(books.count())
#
# for obj in books:
#     print(obj.published_date)




# Q класс

    # SQL        ORM
    # OR      Q() | Q()
    # AND     Q() & Q()
    # NOT        ~Q()



# Найти книги-бестселлеры, опубликованные после 2021 года


# bestsellers = Book.objects.filter(
#     Q(is_bestseller=True) & Q(published_date__gt="2021-01-01")
# )
#
# print(bestsellers.query)
#
#
# for obj in bestsellers:
#     print(obj.is_bestseller, obj.published_date)



# bestsellers = Book.objects.filter(
#     (Q(is_bestseller=True) & Q(published_date__gt="2015-01-01")) | Q(category="Biography")
# )
#
# print(bestsellers.query)
#
#
# for obj in bestsellers:
#     print(obj.is_bestseller, obj.published_date)



# bestsellers = Book.objects.filter(
#     Q(comment__isnull=True) | Q(price__gte=15)
# )
#
# print(bestsellers.query)
#
#
# for obj in bestsellers:
#     print(obj.is_bestseller, obj.published_date)



# (Q или Q) и Q
# bestsellers = Book.objects.filter(
#     (~Q(comment__isnull=False) | Q(is_bestseller=True)) & Q(published_date__range=["2020-01-01", "2026-01-01"])
# ) # Дай мне книги, у которых И (комментарий отсутствует, ИЛИ книга -- бестселлер), И книга была опубликована с 2020 по 2026 года
#
# print(bestsellers.query)
#
#
# for obj in bestsellers:
#     print(obj.is_bestseller, obj.published_date)





# Соранение объектов

# save()
# one_book = Book.objects.get(title="The Hobbit")
#
# print(one_book)
#
# one_book.is_bestseller = True
# one_book.price = Decimal("30.0")
#
# one_book.save()


# one_book = Book.objects.get(title="The Hobbit")
# print(one_book)
# new_data = {
#     "is_bestseller": False,
#     "price": Decimal("11.33")
# }
#
# for column, value in new_data.items():
#     # print(column, value)
#     setattr(one_book, column, value)
#
# one_book.save()



# na_books = Book.objects.filter(
#     category="N/A"
# ).update(category="Fantasy") # update применит ОДНИ И ТЕ ЖЕ значение КО ВСЕМ НАЙДЕНЫМ ОБЪЕКТАМ
#
# print(na_books)


# all_books = Book.objects.all()
#
#
# for book in all_books:
#     disc_price = book.price * .8
#     book.discounted_price = disc_price
#     book.save()


# Book.objects.all().update(
#     discounted_price=F('price') * Decimal("0.8")
# )



# Найти те книги, у которых цена со скидкой больше оригинальной цены
# defected_price = Book.objects.filter(
#     price__lt=F('discounted_price')
# )
#
# print(defected_price.query)
#
# for obj in defected_price:
#     print(f"{obj.discounted_price=}  {obj.price=}")
#



# Delete


# one_book = Book.objects.get(id=281)
#
# one_book.delete()

# CREATE
# Book.objects.create()
#
# book = Book(...)
# book.save()

# READ
# .get() - получить один обхъект (!!!!!!! ObjectDoesNotExist | MultipleObjectsReturned !!!!!!!!!!!)
# .all() - получить все объекты
# .filter() - получить все объекты по фильтр условию
# .exclude() - ИСКЛЮЧИТЬ все объекты по фильтр условию
# .first() - получить первый элемент из кверисета
# .last() - получить последний элемент из кверисета
# .count() - получить количество элементов в кверисете
# .exists() - проверить наличие элементов в кверисете
# .order_by() - задаёт сортировку кверисету


# QuerySet


from my_app.models import Author


# filter_authors = Author.objects.filter(username="qweqweqweqweqweqwe")  # SELECT * FROM 'authors'
# all_authors = Author.objects.all()
# exclude_authors = Author.objects.exclude(username="qwerty")
#
#
# # sorted_authors = all_authors.order_by()
#
# print(type(filter_authors))
# print(type(all_authors))
# print(type(exclude_authors))


from django.db.models import Q

# SQL       Django
# OR       Q() | Q()
# AND      Q() & Q()
# NOT      ~Q() | ~Q()

books = Book.objects.filter(
    Q(Q(category__iexact='fantasy') | ~Q(is_bestseller=True)) & Q(published_date__year__gt=2017)
)


print(books.query)
print(books)
