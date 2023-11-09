from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# LoginRequiredMixin : 장고에서 제공하는 클래스로 view.py에서 임포트하고 사용한다. 매개변수로 추가하면 로그인했을 때만 페이지가 보이게 된다.
from .models import Post, Category, Tag
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify

# from blog.service.blog_service import (
#     post_list_service,
# )  # service layer

# Create your views here.
class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context

    # template_name = 'blog/index.html'

# def index(request):
#     posts = Post.objects.all().order_by('-pk')  # 최신 포스트부터 보여주기

#     return render(
#         request,
#         'blog/index.html',
#         {
#             'posts': posts,
#         }
#     )


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()  # 직속 부모 클래스의 메소드를 사용하기 위함
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context

# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)

#     return render(
#         request,
#         'blog/single_post_page.html',
#         {
#             'post': post,
#         }
#     )


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):  # submit 버튼을 클릭 할 때 동작
        current_user = self.request.user  # 웹 사이트의 방문자

        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):  # is_authenticated로 방문자가 로그인한 상태인지 아닌지 확인
            form.instance.author = current_user  # 로그인 한 상태라면 form에서 생성한 instance(새로 생성한 포스트)의 author 필드에 current_user를 담는다.
            response = super(PostCreate, self).form_valid(form)  # 태그와 관련된 작업을 하기 전에 CreateView의 form_valid() 함수의 결과값을 response에 저장

            tags_str - self.request.POST.get('tags_str')  # 장고가 자동으로 작성한 post_form.html의 폼을 보면 메소드가 post로 설정되어 있다. 이 폼 안에 name='tags_str'인 input을 추가했으니 방문자가 submit 버튼을 클릭했을 때 이 값 역시 post 방식으로 PostCreate까지 전달되어 있는 상태이다. 이 값은 self.request.POST.get('tags_str')로 받을 수 있다. post 방식으로 전달된 정보 중 name='tags_str'인 input의 값을 가져오라는 뜻이다.

            if tags_str:  # 이 값이 빈칸인 경우에는 태그와 관련된 어떤 동작도 할 필요가 없다. tag_str이 존재한다면 여러 개의 태그가 들어오더라도 처리할 수 있어야 하고, 세미콜론과 쉼표 모두 구분자로 처리되어야 한다. tags_str로 받은 값의 쉼표를 세미콜론으로 모두 변환한 후 세미콜론으로 split하여 리스트 형태로 저장한다.
                tags_str = tags_str_strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()  # tags_list에 담겨있는 값들은 문자열 형태이므로 Tag 모델의 인스턴스로 변환하는 과정이 필요하다. 문자열 앞뒤로 공백이 있을 수 있으므로 strip()으로 앞뒤의 공백을 제거한다.
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)  # 위의 값을 name으로 갖는 태그가 있다면 가져오고, 없다면 새로 만든다. get_or_create()는 두 가지 값을 동시에 return한다. 첫 번째는 Tag 모델의 인스턴스이고, 두 번째는 이 인스턴스가 새로 생성되었는지를 나타내는 bool 형태의 값이다.

                    if is_tag_created:  # 만약 같은 name을 갖는 태그가 없어 새로 생성했다면 아직 slug 값은 없는 상태이므로 slug 값을 생성해야 한다. 관리자 페이지에서 작업할 때는 자동으로 생성해줬지만 이번에는 get_or_create() 메서드로 생성했기 때문에 발생하는 문제이다. 이런 경우를 위해 장고는 slugify()라는 함수를 제공한다. 한글 태그가 입력되더라도 slug를 만들 수 있도록 allow_unicode=True로 설정한다. 이 값을 태그의 slug에 부여하고 저장하면 name, slug 필드를 모두 채운 상태로 저장된다. slugify()를 쓰기위해 파일 상단에 import 해준다.
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)  # 새로 태그를 만들었든, 기존에 존재하던 태그를 가져왔든 새로 만든 포스트의 tags 필드에 추가해야 한다. 이때 self.object는 이번에 새로 만든 포스트를 의미한다.

            return response  # 원하는 작업이 다 끝나면 새로 만든 포스트의 페이지로 이동해야 하므로 response 변수에 담아뒀던 CreateView의 form_valid() 결과값을 return한다.

        else:
            return redirect('/blog/')  # 로그인 하지 않은 경우 /blog/ 경로로 리다이렉트


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()

        if self.object.tags.exists():
            tags_str_list = list()

            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')

        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_Str = tags_str.split(';')

            for t in tags_str:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)

                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)  # url에서 인자로 넘어온 slug와 동일한 slug를 가진 태그를 쿼리셋으로 가져와 tag라는 변수에 저장한다.
    post_list = tag.post_set.all()  # 그리고 가져온 태그에 연결된 포스트 전체를 post_list에 저장한다.

    return render(  # 위에서 가져온 인자를 render() 함수 안에 딕셔너리 형태로 넣는다.
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),  # 태그 페이지 오른쪽에도 카테고리 카드를 보여주기 위해 categories와
            'no_category_post_count': Post.objects.filter(category=None).count(),  # no_category_post_count도 다음과 같이 추가한다.
        }
    )