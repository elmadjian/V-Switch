import gi
from gi.repository import Gtk

class Handler:
    def on_main_window_delete_event(self, *args):
        Gtk.main_quit()

class Example:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(Handler())

        window = self.builder.get_object("window1")
        window.show_all()

    def main(self):
        Gtk.main()

x = Example()
x.main()