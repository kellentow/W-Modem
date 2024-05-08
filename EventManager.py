class EventManager:
    def __init__(self):
        self.event_handlers = {}

    def register(self, event_name):
        """
        Registers a callback function to be called when the specified event is triggered.

        Args:
            event_name (str): The name of the event to listen for.
            callback (callable): The function to be called when the event is triggered.

        Raises:
            ValueError: If the specified event does not exist.
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []

    def listen(self, event_name, callback):
        if event_name in self.event_handlers:
            self.event_handlers[event_name].append(callback)
        else:
            raise ValueError(f"Event '{event_name}' does not exist.")
        
    def trigger(self, event_name):
        """
        Triggers the specified event, calling all registered callback functions for that event.

        Args:
            event_name (str): The name of the event to trigger.

        Raises:
            ValueError: If the specified event does not exist.
        """
        if event_name in self.event_handlers:
            for callback in self.event_handlers[event_name]:
                callback()
        else:
            ValueError(f"Event '{event_name}' does not exist.")