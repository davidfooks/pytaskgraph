from pytaskgraph.taskgraph import TaskGraph
from pytaskgraph.task import Task
from pytaskgraph.filedependency import FileDependency

from threading import BoundedSemaphore, Timer
from multiprocessing import cpu_count

def test_1():
    semaphore = BoundedSemaphore(value=cpu_count())
    task_graph = TaskGraph('test1', 'build', semaphore)

    tests_run = {}
    tests_completed = {}

    def run_task(task):
        tests_run[task.name] = True
        def delay_completion():
            tests_completed[task.name] = True
        timer = Timer(1, delay_completion)
        timer.start()
        timer.join()

    task_a = Task(
        name = 'task a',
        rule = run_task,
        src = [FileDependency('test.py')],
        always_build = True
    )

    task_b = Task(
        name = 'task b',
        rule = run_task,
        src = [FileDependency('test.py')],
        always_build = True
    )

    task_graph.add_task(task_a)
    task_graph.add_task(task_b)

    task_graph.execute()

    try:
        if (tests_run['task a'] and
           tests_run['task b'] and
           tests_completed['task b'] and
           tests_completed['task b']):
            print 'pass'
        else:
            print 'fail'
    except KeyError:
        print 'fail'

def test_2():
    semaphore = BoundedSemaphore(value=cpu_count())
    task_graph = TaskGraph('test2', 'build', semaphore)

    def run_copy_task(task):
        def delay_completion():
            src_file = open(task.src[0].path, 'rt')
            dst_file = open(task.dst[0].path, 'wt')
            dst_file.write(src_file.read())
            dst_file.close()
            src_file.close()
        timer = Timer(1, delay_completion)
        timer.start()
        timer.join()

    def run_b(task):
        src_file = open(task.src[0].path, 'rt')
        print(src_file.read())
        src_file.close()

    test_output = FileDependency('text-output.txt')

    task_a = Task(
        name = 'task a',
        rule = run_copy_task,
        src = [FileDependency('test.txt')],
        dst = [test_output]
    )

    task_b = Task(
        name = 'task b',
        rule = run_b,
        src = [test_output]
    )

    task_graph.add_task(task_a)
    task_graph.add_task(task_b)

    task_graph.execute()

def main():
    print 'test 1:'
    test_1()
    print
    print 'test 2:'
    test_2()

if __name__ == '__main__':
    main()
