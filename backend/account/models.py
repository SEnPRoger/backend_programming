from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import shutil
from pathlib import Path
import bcrypt

class AccountManager(BaseUserManager):
    def create_user(self, username, nickname, email, birth_date=None, account_photo=None, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            nickname=nickname,
            account_photo=account_photo,
            birth_date = birth_date,
        )

        # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # user.password = hashed_password.decode('utf-8')

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            nickname=nickname,
            birth_date=None,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

def username_photo_path(instance, filename):
        # file will be uploaded to media/accounts/account.id/username.extension,
        #                     like media/accounts/1/SEnPRoger.jpg
        extension = filename.split('.')[1]
        return 'accounts/{0}/{1}.{2}'.format(instance.id, instance.nickname, extension)

# Create your models here.
class Account(AbstractBaseUser):
    # important info
    nickname            = models.CharField(verbose_name='👤 Nickname', max_length=32, blank=False, unique=True, help_text='Nickname should be unique')
    email               = models.EmailField(verbose_name='📬 Email', max_length=32, blank=False, unique=True, help_text='Email should be unique')

    # personal info
    username            = models.CharField(verbose_name='👤 Username', max_length=32, blank=False)
    birth_date          = models.DateField(verbose_name='🥳 Birth date', blank=True, null=True)
    changed_nickname    = models.DateTimeField(verbose_name='Changed nickname date', default=timezone.now, help_text='Nickname can be changed every 24 hours')

    account_photo       = models.ImageField(verbose_name='🖼 Change account photo', upload_to=username_photo_path, blank=True, null=True)
    account_banner      = models.ImageField(verbose_name='Change account banner', upload_to=username_photo_path, blank=True, null=True)
    
    city                = models.CharField(verbose_name = '🏡 City', max_length=64, blank=True, null=True)
    country             = models.CharField(verbose_name = '🏙 Country', max_length=64, blank=True, null=True)
    links               = models.TextField(verbose_name = '🏙 Social links', blank=True, null=True)

    # stats
    subscribers         = models.ManyToManyField("self", verbose_name = 'Subscribers', blank=True, null=True, related_name='subscribers_set', 
                                                    symmetrical=False)
    blocked_accounts    = models.ManyToManyField("self", verbose_name = 'Blocked accounts', blank=True, null=True, related_name='blocked_accounts_set', 
                                                    symmetrical=False)
    related_posts       = models.ManyToManyField('post.Post', verbose_name = 'Published posts', blank=True, related_name='posts_set')

    # roles
    is_verify           = models.BooleanField(verbose_name = 'Is verified account 💼', default=False)
    is_blocked          = models.BooleanField(verbose_name = '⛔️ Is account blocked', default=False)
    is_moderator        = models.BooleanField(verbose_name = '🛠 Is moderator', default=False)
    is_active           = models.BooleanField(default=True)
    is_admin            = models.BooleanField(verbose_name = '💠 Is admin', default=False)

    # dates
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    objects = AccountManager()

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['email', 'username']

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="150" height="150" style="border-radius: 50%%"; />' % (self.account_photo.url))
    image_tag.short_description = '🖼 Account photo'
    image_tag.allow_tags = True

    def get_image(self):
        if self.account_photo:
            return self.account_photo.url
        
    def image_tag_banner(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="791" height="150" style="border-radius: 20px"; />' % (self.account_banner.url))
    image_tag_banner.short_description = '🖼 Account banner'
    image_tag_banner.allow_tags = True

    def get_image_banner(self):
        if self.account_banner:
            return self.account_banner.url

    def get_subcribers_count(self):
        return self.subscribers.count()
    
    def get_posts_count(self):
        return self.related_posts.count()

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_image = self.account_photo
            self.account_photo = None
            super(Account, self).save(*args, **kwargs)
            self.account_photo = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super(Account, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        try:
            if self.account_photo != None:
                photo_path = Path(self.account_photo.path)
                photo_folder = photo_path.parent
                shutil.rmtree(photo_folder)
        except:
            pass
        super().delete()