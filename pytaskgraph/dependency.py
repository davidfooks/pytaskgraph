class Dependency():

    def __init__(self, name):
        self.name = name

        # the task node that generates the dependency
        self.generated_by = None
        self.hash = None
        self._changed = False


    def changed(self):
        self._changed = True


    def get_hash(self):
        if self._changed or self.hash is None:
            self._changed = False
            self.hash = self.calculate_hash()
        return self.hash


    def calculate_hash(self):
        return self.hash
