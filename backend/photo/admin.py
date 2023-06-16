from django.contrib import admin
from photo.models import Photo
from django.utils import timezone

# Register your models here.
class PhotoAdmin(admin.ModelAdmin):

    @admin.display(description='Photo author')
    def get_author_username(self, obj):
        return obj.author.nickname
    
    @admin.display(description='Published date')
    def get_published_date(self, obj):
        return timezone.localtime(obj.upload_date).strftime('%d %B %Y %H:%M')
    get_published_date.admin_order_field = 'published_date'

    @admin.display(description='Photo author')
    def get_filename(self, obj):
        return obj.file.url
    
    list_display = ('get_filename', 'get_author_username', 'get_published_date', 'id')
    fields = ('file', 'author',)
    #readonly_fields = ('image_tag', 'author', 'get_published_date',)
    list_filter = ('upload_date',)
    ordering = ('upload_date',)

admin.site.register(Photo, PhotoAdmin)