# Generated by Django 4.2.1 on 2023-06-08 16:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=35, verbose_name='Назва посту')),
                ('content', models.CharField(max_length=600, verbose_name='Вміст посту')),
                ('published_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публікації')),
                ('its_reply', models.BooleanField(default=False, verbose_name='Чи це є репост')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='author_set', to=settings.AUTH_USER_MODEL, verbose_name='Автор публікації')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reply_set', to='post.post', verbose_name='Відповідь на пост')),
            ],
        ),
    ]
