from django.contrib import admin
from django.utils import timezone
from post.models import Post
from django.template.defaultfilters import truncatechars  # or truncatewords

# Register your models here.
class PostAdmin(admin.ModelAdmin):

    @admin.display(description='Published date')
    def get_published_date(self, obj):
        return timezone.localtime(obj.published_date).strftime('%d %B %Y %H:%M')
    get_published_date.admin_order_field = 'published_date'

    @admin.display(description='Post author')
    def get_author_username(self, obj):
        return obj.author.nickname
    
    @admin.display(description='Короткий вміст')
    def get_short_content(self, obj):
        return truncatechars(obj.content, 100)

    list_display = ('header', 'get_short_content', 'get_author_username', 'get_published_date', 'id')
    readonly_fields = ('get_published_date', 'get_short_content', 'image_tag', 'is_reply')

    fieldsets = (
        ('Загальна інформація', {
            'fields': ('header', 'content', 'author', 'get_published_date', 'is_edited'),
        }),
        ('Медіа', {
            'fields': ('image', 'image_tag', 'photos'),
        }),
        ('Відповіді та лайки', {
            'fields': ('reply', 'is_reply'),
        }),
    )

    list_filter = ('published_date',)
    ordering = ('published_date',)

admin.site.register(Post, PostAdmin)