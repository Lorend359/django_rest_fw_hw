from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Создаёт группу 'Модераторы', если она ещё не существует."""

    help = "Создаёт группу Модераторы"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Модераторы")
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модераторы" создана'))
        else:
            self.stdout.write('Группа "Модераторы" уже существует')
