from django.template.defaultfilters import truncatechars  # or truncatewords
from django.db import models
from account.models import Account
from photo.models import Photo
import shutil
from pathlib import Path

def post_photo_path(instance, filename):
        # file will be uploaded to media/accounts/account.id/username.extension,
        #                     like media/accounts/1/SEnPRoger.jpg
        extension = filename.split('.')[1]
        return 'posts/{0}/{1}.{2}'.format(instance.id, instance.author.nickname, extension)

# def generate_unique_slug(instance):


# Create your models here.
class Post(models.Model):
    header          = models.CharField(verbose_name='Назва посту', blank=False, max_length=35)
    content         = models.CharField(verbose_name='Вміст посту', blank=False, max_length=600)
    image           = models.ImageField(verbose_name='🖼 Change post photo',
                                             upload_to=post_photo_path, blank=True, null=True)

    author          = models.ForeignKey('account.Account', verbose_name='Автор публікації',
                                         related_name='author_set', on_delete=models.DO_NOTHING)
    published_date  = models.DateTimeField(verbose_name='Дата публікації', auto_now_add=True)
    is_edited = models.BooleanField(verbose_name='Пост було редаговано', default=False)

    reply           = models.ForeignKey('self', verbose_name='Відповідь на пост', related_name='reply_set',
                                         blank=True, null=True, on_delete=models.SET_NULL)
    is_reply = models.BooleanField(verbose_name='Чи це є репост', default=False)
    photos = models.ManyToManyField('photo.Photo', verbose_name='Фотографії', blank=True)

    def __str__(self):
        return self.header
    
    @property
    def short_content(self):
        return truncatechars(self.content, 100)
    short_content.fget.short_description = 'Короткий вміст'

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="460" height="259" style="border-radius: 20px"; />' % (self.image.url))
    image_tag.short_description = '🖼 Post image'
    image_tag.allow_tags = True

    def get_image(self):
        if self.image:
            return self.image.url

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_image = self.image
            self.image = None
            super(Post, self).save(*args, **kwargs)
            self.image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super(Post, self).save(*args, **kwargs)
        account = Account.objects.get(id=self.author.id)
        account.related_posts.add(self)
        super(Account, account).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        try:
            if self.image != None:
                photo_path = Path(self.image.path)
                photo_folder = photo_path.parent
                shutil.rmtree(photo_folder)
        except:
            pass
        super().delete()