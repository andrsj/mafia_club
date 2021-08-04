import logging


class MessageBus:
    """
    This is temprorary class for event bus
    As I dont need eventstore right now
    """

    def __init__(self):
        self._mapped_events = {}

    def register(self, evt, handler):
        self._mapped_events[evt] = handler

    def publish(self, evt):
        handler = self._mapped_events.get(evt.__class__)
        if not handler:
            logging.info(f"Unmapped event f{evt}")
        handler_instance = handler()
        handler_instance.__call__(evt)
