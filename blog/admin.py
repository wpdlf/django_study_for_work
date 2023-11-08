from django.contrib import admin
from .models import Post, Category, Tag

# Register your models here.
admin.site.register(Post)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # Category 모델의 name 필드에 값이 입력됐을 때 자동으로 slug가 만들어진다.

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # name 필드를 이용해 slug를 자동으로 채워주는 코드

admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)