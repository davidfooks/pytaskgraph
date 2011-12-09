# connects tasks by their dependecies
class TaskNode():

    def __init__(self, task, old_hashes):
        self.task = task
        parents = []
        children = []

        dst = task.dst
        src = task.src

        for s in src:
            if s.generated_by is not None:
                children.append(s.generated_by)

        for d in dst:
            if d.generated_by is not None:
                raise Exception('dstput %s for task %s already generated by another task %s' %
                                (d.name, task.name, d.generated_by.name))
            d.generated_by = self

        self.parents = parents
        self.children = children
        self.hashes = old_hashes


    def sources_changed(self):
        new_hashes = self.get_new_hashes()
        new_keys = new_hashes.keys()
        try:
            for src_name in self.hashes:
                if self.hashes[src_name] != new_hashes[src_name]:
                    return True
                new_keys.remove(src_name)

            return len(new_keys) != 0

        except KeyError:
            return True


    def get_new_hashes(self):
        return dict([(unicode(s.name), unicode(s.get_hash())) for s in self.task.src])
