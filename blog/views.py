from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost


def blog_list(request):
    """Blog list page view displaying published blog posts"""
    # Get all published blog posts ordered by publication date
    blog_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    
    # Handle search functionality if search query is provided
    search_query = request.GET.get('search', '')
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Pagination - 9 posts per page
    paginator = Paginator(blog_posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blog_posts': page_obj,
        'search_query': search_query,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'blog.html', context)
