from zlo.adapters.infrastructure import MessageBus
from zlo.domain.events import CreateOrUpdateGame
from zlo.domain.handlers import CreateOrUpdateGameHandler


def map_handlers(bus: MessageBus):
    bus.register(CreateOrUpdateGame, CreateOrUpdateGameHandler)
