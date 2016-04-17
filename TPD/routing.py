from channels import route, include

composition_routing = [
    route(
        'websocket.connect',
        'api.consumers.base.pass_message',
        path=r'/(?P<composition_id>\d+)/'
    ),
    route(
        'websocket.receive',
        'api.consumers.composition.ws_receive',
        path=r'/(?P<composition_id>\d+)/'
    ),
    route(
        'websocket.disconnect',
        'api.consumers.composition.ws_disconnect',
        path=r'/(?P<composition_id>\d+)/'
    ),
]


chat_routing = [
    route('websocket.connect', 'api.consumers.base.pass_message'),
    route('websocket.receive', 'api.consumers.composition.ws_receive'),
    route('websocket.disconnect', 'api.consumers.composition.ws_disconnect'),
]

main_routing = [
    # TODO поправить в настройках nginx
    include(composition_routing, path=r'^/ws/composition'),
    include(chat_routing, path=r'^/ws/chat'),
    route('websocket.connect', 'api.consumers.base.not_found'),
]