from channels import include, route

from api.views.web_socket import ChatSocketView, CompositionSocketView

composition_routing = [
    route('websocket.connect', CompositionSocketView.as_view()),
    route('websocket.receive', CompositionSocketView.as_view()),
    route('websocket.disconnect', CompositionSocketView.as_view()),
]


chat_routing = [
    route('websocket.connect', ChatSocketView.as_view()),
    route('websocket.receive', ChatSocketView.as_view()),
    route('websocket.disconnect', ChatSocketView.as_view()),
]

not_found_routing = [
    route('websocket.connect', 'api.consumers.base.pass_message'),
    route('websocket.receive', 'api.consumers.base.pass_message'),
    route('websocket.disconnect', 'api.consumers.base.pass_message'),
]

main_routing = [
    # TODO поправить в настройках nginx
    include(composition_routing, path=r'^/ws/composition/(?P<composition_id>\d+)/$'),
    include(chat_routing, path=r'^/ws/chat/(?P<band_id>\d+)/$'),
    include(not_found_routing),
]
