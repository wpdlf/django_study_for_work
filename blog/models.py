from django.db import models
from django.contrib.auth.models import User
import os

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):  # 해당 클래스로 만들어진 인스턴트 자체를 출력할 때, 문자열로 설명해주기 위한 메서드이다.
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        # 복수형
        verbose_name_plural = 'Categories'  # admin 페이지 내의 자동으로 설정된 'Categorys'를 'Categories'로 변경


class Post(models.Model):
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # author = models.ForeignKey(User, on_delete=models.CASECADE)  # 작성자가 삭제되면 해당 작성자가 작성한 포스트도 삭제
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)  # 작성자가 삭제되면 해당 작성자가 작성한 포스트에 작성자를 빈 칸으로 둔다.

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)  # ManyToManyField는 기본적으로 null=True가 설정되어 있어 따로 입력한 null=True는 효과가 없다.

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]