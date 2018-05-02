from django.conf.urls import url
from . import views

#views
urlpatterns = [
    # Post views
    url(r'^$', views.post_list, name = 'post_list'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'\
        r'(?P<slug>[-\w]+)/$',
        views.post_detail, name = 'post_detail'),
    url(r'^(?P<post_id>\d+)/share/$', views.post_share, name = 'post_share'),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list, name = 'post_list_by_tags'),
    #url(r'^$', views.PostListView.as_view(), name = 'post_list'),
    url(r'^add_post', views.AddPostView.as_view(), name = 'add_post')
]
