from pytaskgraph.utils import mkdir
from pytaskgraph.tasknode import TaskNode

from os.path import abspath, normcase, join as join_path
from json import dump, load

# TODO: implement cycle check
class TaskGraph():

    def __init__(self, name, build_dir, max_threads_semaphore):
        self.task_nodes = []
        self.running_tasks = []
        self.name = name

        build_dir = normcase(abspath(build_dir))
        mkdir(build_dir)

        hashes_file_path = join_path(build_dir, name + '-nodes.json')
        self.hashes_file_path = hashes_file_path

        try:
            hashes_file = open(hashes_file_path, 'rt')
            self.node_hashes = load(hashes_file, 'utf-8')
            hashes_file.close()
        except (IOError, ValueError):
            self.node_hashes = {}

        self.build_dir = build_dir
        self.max_threads_semaphore = max_threads_semaphore


    def add_task(self, task):
        task.task_graph = self

        node = TaskNode(task, self.node_hashes.get(task.name, {}))
        task.node = node
        self.task_nodes.append(node)


    @classmethod
    def parse_nodes(cls, nodes):
        leaf_nodes = []
        waiting_nodes = []

        task_nodes = nodes
        for node in task_nodes:
            task = node.task

            if task.is_waiting():
                # if all dependent tasks are complete then this task is ready
                is_leaf = True
                for child_node in node.children:
                    if not child_node.task.is_complete():
                        is_leaf = False
                        break

                if is_leaf:
                    if node.sources_changed() or task.always_build:
                        leaf_nodes.append(node)
                    else:
                        task.sources_unchanged()
                else:
                    waiting_nodes.append(node)
        return leaf_nodes, waiting_nodes


    # beware this function will sometimes hang before completion
    def schedule_task(self, task):
        self.running_tasks.append(task)
        print 'running task ' + task.name
        task.start(self.max_threads_semaphore)

        for task in self.running_tasks:
            if task.is_complete():
                self.running_tasks.remove(task)


    def generate_tree(self):
        for node in self.task_nodes:
            task = node.task
            for src in task.src:
                generated_by = src.generated_by
                if generated_by is not None:
                    node.children.append(generated_by)
                    generated_by.parents.append(node)


    # this function hangs until execution is complete
    def execute(self):
        self.generate_tree()

        waiting_nodes = self.task_nodes
        while True:
            leaf_nodes, waiting_nodes = self.parse_nodes(waiting_nodes)
            for task_node in leaf_nodes:
                self.schedule_task(task_node.task)
            if len(leaf_nodes) + len(waiting_nodes) == 0:
                break

        # actach to any remaining threads to make sure everything has finished
        for task in self.running_tasks:
            task.join()

        new_node_hashes = {}
        for task_node in self.task_nodes:
            new_node_hashes[task_node.task.name] = task_node.get_new_hashes()

        node_hashes_file = open(self.hashes_file_path, 'w')
        dump(new_node_hashes, node_hashes_file)
        node_hashes_file.close()

