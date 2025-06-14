import logging

from django_q.tasks import AsyncTask, Schedule

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Base class to model work that is processed asynchronously via a task queue, on some schedule.

    Attributes:

      count (int): How many concurrent scheduled tasks can exist at once.
      cron (str): The CRON expression that defines this task's schedule; setting this also uses `ScheduledTask.CRON`.
      group (str): An identifier that can be used to aggregate results from related tasks.
      minutes (int): When using `ScheduledTask.MINUTES`, this value is the increment; ignored otherwise.
      name (str): The specific name of this task.
      repeats (int): Number of times to repeat the schedule:
        -1=Always, 0=Never, n=N times
      schedule_type (str): one of the types on `ScheduledTask`:
        ONCE, MINUTES, HOURLY, DAILY, WEEKLY, BIWEEKLY, MONTHLY, BIMONTHLY, QUARTERLY, YEARLY, CRON

    Usage:

        # https://django-q2.readthedocs.io/en/master/schedules.html#django_q.Schedule

        from web.core.tasks import ScheduledTask

        class MyScheduledTask(ScheduledTask):
            group = "my-group"
            name = "my-task"
            count = 1

            # use a cron expression
            cron = "*/5 * * * *"  # every 5 minutes

            # OR equivalently, use minutes, and the ScheduledTask.MINUTES type
            minutes = 5
            schedule_type = ScheduledTask.MINUTES

            # OR e.g. another fixed schedule type
            schedule_type = ScheduledTask.DAILY

            @classmethod
            def handler(cls, *args, **kwargs):
                # Perform the work for this task
                # Called on this task's schedule
                self.do_something(self.some_prop)

            @classmethod
            def post_handler(cls, *args, **kwargs):
                # Optional hook performs work after this task completes
                pass

        # ... elsewhere ...

        # create a task instance and schedule it immediately
        MyScheduledTask.create(some_arg="the-data")
    """

    cron = ""
    count = 1
    group = "disaster-recovery"
    minutes = 0
    name = "schedule"
    repeats = -1
    schedule_type = ""

    ONCE = Schedule.ONCE
    CRON = Schedule.CRON
    MINUTES = Schedule.MINUTES
    HOURLY = Schedule.HOURLY
    DAILY = Schedule.DAILY
    WEEKLY = Schedule.WEEKLY
    BIWEEKLY = Schedule.BIWEEKLY
    MONTHLY = Schedule.MONTHLY
    BIMONTHLY = Schedule.BIMONTHLY
    QUARTERLY = Schedule.QUARTERLY
    YEARLY = Schedule.YEARLY

    @classmethod
    def group_name(cls):
        return f"{cls.group}:{cls.name}"

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs["cron"] = kwargs.pop("cron", cls.cron)
        kwargs["minutes"] = kwargs.pop("minutes", cls.minutes)
        name = kwargs.pop("name", cls.group_name())
        kwargs["name"] = name
        kwargs["repeats"] = kwargs.pop("repeats", cls.repeats)
        kwargs["schedule_type"] = kwargs.pop("schedule_type", cls.schedule_type)

        if kwargs["cron"]:
            kwargs["schedule_type"] = cls.CRON

        # both func and hook need to be dotted string paths
        # https://django-q2.readthedocs.io/en/master/schedules.html#reference

        # use __qualname__ to get the fully qualified dotted path to each function
        # https://docs.python.org/3/glossary.html#term-qualified-name
        kwargs["func"] = f"{cls.__module__}.{cls.handler.__qualname__}"
        kwargs["hook"] = f"{cls.__module__}.{cls.post_handler.__qualname__}"

        target_count = kwargs.pop("count", cls.count)
        actual_count = Schedule.objects.filter(name=name).count()

        if actual_count < target_count:
            Schedule.objects.create(**kwargs)
        else:
            logger.debug(f"{name} already has {target_count}/{actual_count} instance(s) scheduled.")

    @classmethod
    def handler(cls, *args, **kwargs):
        """Perform the work for this task, when it is picked up by a worker from a queue."""
        logger.debug(f"Handling task: {cls.group_name()}")

    @classmethod
    def post_handler(cls, *args, **kwargs):
        """Optional hook performs work after this task completes. Often used to add a follow-up task to the queue."""
        logger.debug(f"Post handler for task: {cls.group_name()}")


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
