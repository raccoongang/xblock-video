"""
videojs_app URL Configuration.
"""
from django.conf.urls import url
from views import player_list, detail, player
urlpatterns = [
    url(r'^$', player_list, name='list'),
    url(r'^player/(?P<player_name>[a-z0-9]+)$', player, name='player'),
    url(r'^(?P<player_name>[a-z0-9]+)$', detail, name='detail'),

]
