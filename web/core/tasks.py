import logging

from django_q.tasks import AsyncTask

logger = logging.getLogger(__name__)


class Task(AsyncTask):
    group = "disaster-recovery"
    name = "task"

    def __init__(self, *args, **kwargs):
        kwargs["group"] = kwargs.pop("group", self.group)
        kwargs["task_name"] = kwargs.pop("task_name", self.name)
        kwargs["hook"] = self.post_handler
        super().__init__(self.handler, *args, **kwargs)

    def handler(self, *args, **kwargs):
        logger.debug(f"Handling task: {self.name}")

    def post_handler(self, task):
        logger.debug(f"Post handler for task: {task.id}")
