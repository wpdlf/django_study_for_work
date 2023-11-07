from django.contrib import admin
from .models import Post, Category

# Register your models here.
admin.site.register(Post)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # Category 모델의 name 필드에 값이 입력됐을 때 자동으로 slug가 만들어진다.

admin.site.register(Category, CategoryAdmin)