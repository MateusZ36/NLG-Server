from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


def start(nlg_class):
    def on_created(event):
        nlg_class.load_domain()

    def on_deleted(event):
        nlg_class.load_domain()

    def on_modified(event):
        nlg_class.load_domain()

    def on_moved(event):
        nlg_class.load_domain()

    my_event_handler = PatternMatchingEventHandler(["*.yml"])
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved
    my_observer = Observer()
    my_observer.schedule(my_event_handler, nlg_class.domain_path, recursive=True)
    my_observer.start()
