from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Создаёт группу Модераторы'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Модераторы")
        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модераторы" создана'))
        else:
            self.stdout.write('Группа "Модераторы" уже существует')
