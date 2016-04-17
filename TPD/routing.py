from channels import route, include

editor_routing = [
    route('websocket.connect', 'api.consumers.ws_connect', path=r'/(?P<composition_id>\d+)/'),
    route('websocket.receive', 'api.consumers.ws_receive', path=r'/(?P<composition_id>\d+)/'),
    route('websocket.disconnect', 'api.consumers.ws_disconnect', path=r'/(?P<composition_id>\d+)/'),
]


chat_routing = [
    route('websocket.connect', 'api.consumers.ws_connect'),
    route('websocket.receive', 'api.consumers.ws_receive'),
    route('websocket.disconnect', 'api.consumers.ws_disconnect'),
]

main_routing = [
    include(editor_routing, path=r'^/track'),
    include(chat_routing, path=r'^/chat'),
]