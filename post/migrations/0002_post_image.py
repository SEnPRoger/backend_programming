# Generated by Django 4.2.1 on 2023-06-08 16:51

from django.db import migrations, models
import post.models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=post.models.post_photo_path, verbose_name='🖼 Change post photo'),
        ),
    ]
