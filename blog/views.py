# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, CreateView
from .forms import EmailPostForm, CommentForm, PostPageForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.http import HttpResponse

# Create your views here.
def post_list(request, tag_slug=None):
    posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    paginator = Paginator(posts, 3) # 3 post per page
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts' : posts,
        'page' : page,
        'tag' : tag,
    }
    return render(request, 'blog/post/list.html', context)

def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post,
                            slug = slug,
                            status = 'published',
                            publish__year = year,
                            publish__month = month,
                            publish__day = day)

    comments = post.comments.filter(active = True)
    new_comment = ''
    if request.method == 'POST':
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    #Similar Posts
    post_tags_ids = post.tags.values_list('id', flat = True)
    similar_post = Post.published.filter(tags__in = post_tags_ids).exclude(id = post.id)
    similar_post = similar_post.annotate(same_tags = Count('tags')).order_by('-same_tags', '-publish')[:4]

    context = {
        'post' : post,
        'comments' : comments,
        'comment_form' : comment_form,
        'new_comment' : new_comment,
        'similar_post' : similar_post,
    }

    return render(request, 'blog/post/detail.html', context)

#class based view
class AddPostView(CreateView):
    form_class = PostPageForm
    success_url = '/blog/'
    template_name = 'blog/post/add_post.html'

    def form_valid(self, form):
        print self.request.POST['title']
        new_post = form.save(commit = False)
        new_post.author_id = self.request.user.id
        new_post.save()
        return super(AddPostView, self).form_valid(form)

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_share(request, post_id):
    # Get Post by id
    sent = False
    post = get_object_or_404(Post, id = post_id, status = 'published')
    context = {
        'post' : post
    }
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        context['form'] = form
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {} \n\n{}\s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])

            send_mail(subject, message, 'vanarvin.crisostomo@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
        context['form'] = form
        context['sent'] = sent
    return render(request, 'blog/post/share.html', context)
