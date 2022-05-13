from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


def start(nlg_class):
    def load_domain(event):
        nlg_class.load_domain()

    my_event_handler = PatternMatchingEventHandler(["*.yml"])
    my_event_handler.on_created = load_domain
    my_event_handler.on_deleted = load_domain
    my_event_handler.on_modified = load_domain
    my_event_handler.on_moved = load_domain
    my_observer = Observer()
    my_observer.schedule(my_event_handler, nlg_class.domain_path, recursive=True)
    my_observer.start()
