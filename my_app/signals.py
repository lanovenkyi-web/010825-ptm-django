from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction

from my_app.models import Category, User


# @receiver(sender=Category, signal=post_save)
# def category_create_update_signal(sender: Category, instance: Category, created: bool, **kwargs) -> None:
#     if created:
#         print(f"New Category was created with name '{instance.name}'")
#     else:
#         print(f"Category was updated. New name of category is '{instance.name}'")



# ЗАДАЧА: отлавливать старое название категории

@receiver(signal=pre_save, sender=Category)
def track_old_category_name(sender: Category, instance: Category, **kwargs):
    # если инстанса нет (нет его первичного ключа)
    # помечаем в отдельной переменной-хранилище, что старого названия нет
    if not instance.pk:
        instance._old_name = None
        return

    # class_attr --> public attr
    # _class_attr --> private attr
    # __class_attr --> protected attr

    #
    # если всё же инстанс есть -- нужно получить его имя, сохранить в переменной-хранилище
    try:
        old_obj = Category.objects.only('id', 'name').get(pk=instance.pk)
        instance._old_name = old_obj.name
    except Category.DoesNotExist:
        instance._old_name = None


@receiver(signal=post_save, sender=Category)
def category_log_name_legend(sender: Category, instance: Category, created: bool, **kwargs):
    # если объект у нас создаётся
    # старого названия ещё нет, поэтому сразу выходим (ну или делаем базовый принт)
    if created:
        return

    # если всё же объект обновлялся
    # нужно получить старое имя категории
    old_name = instance._old_name

    # получить новое имя категории
    new_name = instance.name

    # на всякий случай проверить себя на изменённое имя
    # категории (действительно ли поменялось ися)

    if not old_name or old_name == new_name:
        return

    # только если старое имя не равно новому -- делать лог / принт (через транзакции)

    def print_name_changes():
        print("=" * 100)
        print(f"Category was update it's name from '{old_name}' to '{new_name}'")
        print("=" * 100)

    transaction.on_commit(print_name_changes)




# РАБОТА С email НОТИФИКАЦИЕЙ ЧЕРЕЗ СИГНАЛЫ


@receiver(pre_save, sender=User)
def store_previous_user_state(sender: User, instance: User, **kwargs) -> None:
    # если пользователь только создаётся -- никаких is_staff и role=moderator у него нет

    if not instance.pk:
        instance._previous_is_staff = None
        instance._previous_role = None
        return

    try:
        old_user_instance = User.objects.only('is_staff', 'role').get(pk=instance.pk)
    except User.DoesNotExist:
        instance._previous_is_staff = None
        instance._previous_role = None
        return

    instance._previous_is_staff = old_user_instance.is_staff
    instance._previous_role = old_user_instance.role


@receiver(signal=post_save, sender=User)
def notify_admins_on_new_staff(
        sender: User,
        instance: User,
        created: bool,
        update_fields: list[str] | None = None,
        **kwargs
) -> None:
    # может быть пользователь итак уже стафф(is_staff=True + роль == moderator) -- выходим
    is_moderator = (
        instance.is_staff
        and
        instance.role == User.Role.moderator
    )

    if not is_moderator:
        return

    # если всё же всё гуд и пользователь лишь сейчас СТАНОВИТСЯ модератором
    # получаем список email аддресов всех админов

    admin_emails = [
        user.email
        for user in User.objects.only('email').filter(is_staff=True, role=User.Role.admin)
    ]

    if created:
        send_mail(
            subject="New staff member in system",
            message=f"New staff member with nickname '{instance.username}' was created.\n\n You can connect with him via his email '{instance.email}'.",
            from_email="no-reply.010825-ptm@gmail.com",
            recipient_list=admin_emails
        )
        return

    moderator_fields = {'is_staff', 'role'}

    if update_fields and not (set(update_fields) & moderator_fields):
        return

    was_moderator = (
        instance._previous_is_staff
        and
        instance._previous_role == User.Role.moderator
    )

    if was_moderator:
        return

    send_mail(
        subject="New staff member in system",
        message=f"New staff member with nickname '{instance.username}' was created.\n\n You can connect with him via his email '{instance.email}'.",
        from_email="no-reply.010825-ptm@gmail.com",
        recipient_list=admin_emails
    )

    # проверяем создавался ли объект или обновлялся.
    # вызвать некий метод на оповещение по email почте(Django test backend server)