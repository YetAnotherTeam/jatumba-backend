from channels import route, include

from api.socket.views import CompositionSocketView

composition_routing = [
    route(
        'websocket.connect',
        'api.consumers.base.pass_message',
        path=r'/(?P<composition_id>\d+)/$'
    ),
    route(
        'websocket.receive',
        CompositionSocketView.as_view(),
        path=r'/(?P<composition_id>\d+)/$'
    ),
    route(
        'websocket.disconnect',
        CompositionSocketView.as_view(),
        path=r'/(?P<composition_id>\d+)/$'
    ),
]


chat_routing = [
    route('websocket.connect', 'api.consumers.base.pass_message'),
    route('websocket.receive', CompositionSocketView.as_view()),
    route('websocket.disconnect', CompositionSocketView.as_view()),
]

not_found_routing = [
    route('websocket.connect', 'api.consumers.base.not_found'),
    route('websocket.receive', 'api.consumers.base.not_found'),
    route('websocket.disconnect', 'api.consumers.base.pass_message'),
]

main_routing = [
    # TODO поправить в настройках nginx
    include(composition_routing, path=r'^/ws/composition'),
    include(chat_routing, path=r'^/ws/chat'),
    include(not_found_routing),
]