from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin  # 장고에서 제공하는 클래스로 view.py에서 임포트하고 사용한다. 매개변수로 추가하면 로그인했을 때만 페이지가 보이게 된다.
from .models import Post, Category, Tag

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

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def form_valid(self, form):
        current_user = self.request.user  # 웹 사이트의 방문자

        if current_user.is_authenticated:  # is_authenticated로 방문자가 로그인한 상태인지 아닌지 확인
            form.instance.author = current_user  # 로그인 한 상태라면 form에서 생성한 instance(새로 생성한 포스트)의 author 필드에 current_user를 담는다.
            return super(PostCreate, self).form_valid(form)  # CreateView의 기본 form_valid() 함수에 현재의 form을 인자로 보내 처리한다.
        else:
            return redirect('/blog/')  # 로그인 하지 않은 경우 /blog/ 경로로 리다이렉트

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