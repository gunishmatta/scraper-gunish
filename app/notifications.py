from app.interfaces import AbstractNotifier


class ConsoleNotifier(AbstractNotifier):
    def notify(self, message: str):
        print(f"Notification: {message}")
