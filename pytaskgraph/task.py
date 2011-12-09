from threading import Thread

class TaskThread(Thread):

    def __init__(self, func, task):
        Thread.__init__(self)
        self.func = func
        self.task = task
        self.semaphore = None

    def run(self):
        self.func(self.task)
        self.task.complete()

        # this semaphore allows us to limit the number of
        # threads running concurrently
        self.semaphore.release()


class Task():

    status_created = 'created'
    status_thread_running = 'thread running'
    status_thread_complete = 'thread complete'
    status_sources_unchanged = 'sources unchanged'

    def __init__(self, name, src=None, dst=None, thread=None, rule=None, env=None, always_build=False):
        self.task_graph = None
        self.node = None

        if src is None:
            src = []
        if dst is None:
            dst = []
        if env is None:
            env = {}
        if thread is None:
            thread = TaskThread(rule, self)

        self.status = self.status_created
        self.env = env
        self.name = name
        self.src = src
        self.dst = dst
        self.thread = thread
        self.always_build = always_build
        thread.task = self


    def complete(self):
        self.status = Task.status_thread_complete
        for d in self.dst:
            d.changed()


    def is_waiting(self):
        return self.status == self.status_created


    def is_complete(self):
        return (self.status == self.status_thread_complete or
                self.status == self.status_sources_unchanged)


    def sources_unchanged(self):
        self.status = self.status_sources_unchanged


    # beware this function will sometimes hang before completion
    def start(self, semaphore):
        thread = self.thread

        # only allow a set number of threads to run concurrently
        # this is released by the thread once it have completed its task
        semaphore.acquire()
        thread.semaphore = semaphore

        self.status = self.status_thread_running
        return thread.start()


    def join(self):
        return self.thread.join()
