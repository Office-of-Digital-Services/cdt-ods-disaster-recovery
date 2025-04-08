import logging

from django_q.tasks import AsyncTask

logger = logging.getLogger(__name__)


class Task(AsyncTask):
    """Base class to model work that is processed asynchronously via a task queue.

    Attributes:

      group (str): An identifier that can be used to aggregate results from related tasks.
      name (str): The specific name of this task.

    Usage:

        # https://django-q2.readthedocs.io/en/stable/tasks.html#asynctask

        from web.core.tasks import Task

        class MyTask(Task):
            group = "my-group"
            name = "my-task"

            def __init__(self, some_arg):
                super().__init__()
                self.some_prop = some_arg

            def handler(self, *args, **kwargs):
                # Perform the work for this task
                # Called when a worker picks up the task from a queue
                self.do_something(self.some_prop)

            def post_handler(self, task):
                # Optional hook performs work after this task completes
                # Often used to add a follow-up task to the queue
                pass

        # ... elsewhere ...

        # create a task instance
        task = MyTask(some_arg="the-data")

        # add it to the queue, a worker will pick it up
        task.run()
    """

    group = "disaster-recovery"
    name = "task"

    def __init__(self, *args, **kwargs):
        kwargs["group"] = kwargs.pop("group", self.group)
        kwargs["task_name"] = kwargs.pop("task_name", self.name)
        kwargs["hook"] = self.post_handler
        super().__init__(self.handler, *args, **kwargs)

    def handler(self, *args, **kwargs):
        """Perform the work for this task, when it is picked up by a worker from a queue."""
        logger.debug(f"Handling task: {self.name}")

    def post_handler(self, task):
        """Optional hook performs work after this task completes. Often used to add a follow-up task to the queue."""
        logger.debug(f"Post handler for task: {task.id}")
