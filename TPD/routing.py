from channels import route, include

editor_routing = [
    route('websocket.connect', 'api.consumers.ws_connect'),
    route('websocket.receive', 'api.consumers.ws_receive'),
    route('websocket.disconnect', 'api.consumers.ws_disconnect'),
]


chat_routing = [
    route('websocket.connect', 'api.consumers.ws_connect'),
    route('websocket.receive', 'api.consumers.ws_receive'),
    route('websocket.disconnect', 'api.consumers.ws_disconnect'),
]

main_routing = [
    include(editor_routing, path=r'^/editor'),
    include(chat_routing, path=r'^/chat'),
    include(chat_routing, path=r''),
]