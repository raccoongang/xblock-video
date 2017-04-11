"""
Django views.
"""
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.shortcuts import render

from utils import get_player, player_data, obj

PLAYER_LIST = settings.PLAYER_DATA.keys()


def player_list(request):
    """
    View with list of players.
    """
    context = {'player_list': PLAYER_LIST}
    return render(request, 'list.html', context)


def player(request, player_name):
    """
    View to render player for iFrame.
    """
    data = player_data(player_name)
    player_cls = get_player(player_name)
    if not player_cls or not data:
        return HttpResponseNotFound(
            '<h1>404 Error. Unsupported player name. Choose one from list: {}</h1>'.format(PLAYER_LIST)
        )

    player = player_cls(obj(data)) if player_name == 'brightcove' else player_cls(data)
    response = player.get_player_html(
        url=data['href'],
        autoplay=False,
        account_id=data.get('account_id', ''),
        player_id='default',
        video_id=player.media_id(data['href']),
        video_player_id='video_player_{}'.format('test_block'),  # pylint: disable=no-member
        save_state_url='',
        player_state={
            'currentTime': 0,
            'transcripts': []
        },
        start_time=0,
        end_time=0,
        brightcove_js_url="https://players.brightcove.net/{account_id}/{player_id}_default/index.min.js".format(
            account_id=data.get('account_id', ''),
            player_id='default'
        ),
        transcripts={},
    )
    return HttpResponse(response.body)


def detail(request, player_name):
    """
    View to render student view imitation.
    """
    data = player_data(player_name)
    player_cls = get_player(player_name)

    if not player_cls or not data:
        return HttpResponseNotFound(
            '<h1>404 Error. Unsupported player name. Choose one from list: %s</h1' % PLAYER_LIST
        )
    context = {
        'player_name': player_name,
    }
    return render(request, 'detail.html', context)
