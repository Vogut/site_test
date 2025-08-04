from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from django.conf import settings
from .models import Blog, BlogType
from read_statistics.utils import get_read_num

def get_blogs_list_common_data(request, blogs_all):
    context = {}
    page_num=request.GET.get("page",1)
    p=Paginator(blogs_all,settings.EACH_PAGE_NUM)
    page_obj = p.get_page(page_num)
    current_page_num=page_obj.number
    page_range=p.get_elided_page_range(current_page_num,on_each_side=1,on_ends=1)
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_date_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_count
    context['blogs'] = page_obj
    context['page_range'] = page_range

    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['blog_dates'] = blog_date_dict
    return context

def blog_list(request):
    
    blogs_all=Blog.objects.all()
    context = get_blogs_list_common_data(request,blogs_all=blogs_all)
    return render(request, 'blog/blog_list.html', context)



def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all=Blog.objects.filter(blog_type=blog_type)
    context = get_blogs_list_common_data(request,blogs_all=blogs_all)

    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)

def blogs_with_date(request,year,month):
    blogs_all = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blogs_list_common_data(request, blogs_all)
    context['blogs_with_date'] = f'{year}年{month}月'
    return render(request, 'blog/blogs_with_date.html', context)

def blog_detail(request, blog_pk):
    context = {}
    blog=get_object_or_404(Blog, pk=blog_pk)
    cookie_key=get_read_num(request,blog)
    context['previous_blog']=Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['next_blog']=Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['blog'] = blog
    response=render(request, 'blog/blog_detail.html', context)
    response.set_cookie(cookie_key,'true')
    return response