class ValidationTracer:
    def __init__(self, enabled=False):
        self.enabled = enabled

    def log(self, message):
        if self.enabled:
            print(message)
