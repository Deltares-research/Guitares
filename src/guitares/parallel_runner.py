from concurrent.futures import ThreadPoolExecutor, wait
import queue
import threading
import logging
from typing import Callable

class Singleton(type):
    """Metaclass to create a singleton class. This is used to make sure only one instance 
    of the ParallelRunner class is created. It also keeps track of how often the class is 
    instantiated. This is used to clean up the executor and the worker thread when the last 
    instance is deleted."""

    _instances = {}
    _counter = 0

    def __call__(cls, *args, **kwargs):
        """Call the class. If the class has not been instantiated before, instantiate it.
        If it has been instantiated before, return the existing instance.

        Parameters
        ----------
        cls : type
            The class to be instantiated
        *args : list
            The arguments to be passed to the class
        *kwargs : dict
            The keyword arguments to be passed to the class

        Returns
        -------
        object
            The instance of the class
        """

        logging.debug("Calling " + cls.__name__)
        if cls not in cls._instances:

            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ParallelRunner(metaclass=Singleton):
    def __init__(self, application, print_debug=False):
        """
        .. warning:: This class itself doesn't provide thread safety. Tasks submitted
        should not be influenced by other tasks or by the main thread. If this is the
        case, the tasks should be made thread safe. For example, if a task writes to a
        file, the file should be locked to prevent other tasks from writing to the file
        at the same time. If a task writes to a variable in the gui, the variable should
        be locked to prevent other tasks from writing to the variable at the same time. 
        This also means that submitting two tasks with the same name, or that point the 
        result to the same variable, will interfere with each other. Only the result of 
        the last task will be written to the variable. If you are concerened about 
        thread safety between tasks, use the submit_task method instead of the 
        submit_parallel_task method. This only guarantees that the tasks are executed 
        sequentially, in parallel with the gui. Thread safety between the tasks and the 
        gui is the responsibility of the user.

        Initialise the parallel runner. This class is used to run tasks in parallel
        with the GUI. The class uses a queue to store the tasks, and a separate thread
        to process the tasks. The tasks are executed in a thread pool of the executor.
        The result of the task is written to the gui if requested.

        Parameters
        ----------
        application : object
            The application object. This is used to access the gui
        print_debug : bool (optional)
            Whether to print debug messages. The default is False

        Attributes
        ----------
        tasks : queue.Queue
            The queue to store the tasks
        executor : concurrent.futures.ThreadPoolExecutor
            The executor to execute the tasks
        shutdown : bool
            Whether the executor is shutting down
        worker_thread : threading.Thread
            The thread to process the tasks
        """ 

        if print_debug:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.WARNING)
        
        logging.debug("Initialising ParallelRunner")

        # Store the application object to write variables to the application
        self.application = application

        # These are required to clean up the executor and the worker thread 
        # when the last instance is deleted. Only cleanup if the executor 
        # has run at least once (otherwise you might cleanup before running something), 
        # when the queue is empty and noting is running (list is empty)
        self.has_run = False
        self.running_tasks = []

        # Initialise the queue, the executor and the worker thread
        self.tasks = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_queued_tasks)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def _process_submitted_tasks(self, task: Callable, *args, **kwargs):
        """Process the tasks in the queue and adds a callback function to the future.
        This function is run in a separate thread. This function is used to submit
        tasks to the executor.
        
        Parameters
        ----------
        task : function
            The function to be executed
        *args : list
            The arguments to be passed to the function
        task_name : str (optional)
            The name of the task. This is used to indicate the status of the task. This wil be written to the gui as {task_name}_status. If not provided, the status will not be monitored.
        write_result : bool (optional)
            Whether to write the result to a variable in the gui. The default is False
        group : str (optional)
            The group of the variable to be set
        name : str (optional)
            The name of the variable to be set
        wait_for_complete : bool (optional)
            Whether to wait for the task to complete before returning. The default is True
        
        Raises
        ------
        ShutDownError
            If the executor is shutting down, no more tasks can be submitted
        ValueError
            If write_result is True, group and name must be provided
        """

        # Get inputs from gui variable dict
        task_name = kwargs.get("task_name", None)
        write_result = kwargs.get("write_result", False)
        group = kwargs.get("group", None)
        name = kwargs.get("name", None)
        wait_for_complete = kwargs.get("wait_for_complete", True)

        # Get inputs from gui variable dict
        if write_result and (not group or not name):
            raise ValueError("If write_result is True, group and name must be provided")

        # If not, submit the task
        self.tasks.put((task, args, task_name, write_result, group, name, wait_for_complete))

    def submit_task(self, task: Callable, *args, **kwargs):
        """Submit a task to the executor. With the current implementation, the task is
        submitted to a queue, and a separate thread is used to process the tasks. The
        task is executed in the thread pool of the executor. The result of the task is
        written to the gui if requested. This method guarantees that the tasks are
        executed sequentially, in parallel with the gui. Thread safety between the tasks
        and the gui is the responsibility of the user.

        Parameters
        ----------
        task : function
            The function to be executed
        *args : list
            The arguments to be passed to the function
        task_name : str (optional)
            The name of the task. This is used to indicate the status of the task. This wil be written to the gui as {task_name}_status. If not provided, the status will not be monitored.
        write_result : bool (optional)
            Whether to write the result to a variable in the gui. The default is False
        group : str (optional)
            The group of the variable to be set
        name : str (optional)
            The name of the variable to be set

        Raises
        ------
        ShutDownError
            If the executor is shutting down, no more tasks can be submitted
        ValueError
            If write_result is True, group and name must be provided
        """

        kwargs["wait_for_complete"] = True
        self._process_submitted_tasks(task, *args, **kwargs)

    def submit_parallel_task(self, task: Callable, *args, **kwargs):
        """Submit a task to the executor. With the current implementation, the task is
        submitted to a queue, and a separate thread is used to process the tasks. The
        task is executed in the thread pool of the executor. The result of the task is
        written to the gui if requested. This method does not guarantee that the tasks
        are executed sequentially. Thread safety between the tasks and the gui but also 
        between the tasks themselves is the responsibility of the user. Also, if submit_task
        is used after this function, the first task submitted by submit_task will be executed
        in parallel with the tasks submitted by this function.

        Parameters
        ----------
        task : function
            The function to be executed
        *args : list
            The arguments to be passed to the function
        task_name : str (optional)
            The name of the task. This is used to indicate the status of the task. This wil be written to the gui as {task_name}_status. If not provided, the status will not be monitored.
        write_result : bool (optional)
            Whether to write the result to a variable in the gui. The default is False
        group : str (optional)
            The group of the variable to be set
        name : str (optional)
            The name of the variable to be set

        Raises
        ------
        ShutDownError
            If the executor is shutting down, no more tasks can be submitted
        ValueError
            If write_result is True, group and name must be provided
        """

        kwargs["wait_for_complete"] = False
        self._process_submitted_tasks(task, *args, **kwargs)


    def _make_callback(self, task_name: str, write_result: bool, group: str, name: str):
        """Make a callback function to be called when the task is done. This function
        will write the result to the gui if requested, and update the status of the task.

        Parameters
        ----------
        task_name : str
            The name of the task
        write_result : bool
            Whether to write the result to the gui
        group : str
            The group of the variable to be set
        name : str
            The name of the variable to be set

        Returns
        -------
        function
            The callback function
        """

        def _process_calback(future):
            """The callback function. This function will write the result to the gui if requested, and update the status of the task.

            Parameters
            ----------
            future : concurrent.futures.Future
                The future object of the task
            """
            # This code will be run when the future is done
            if task_name:
                if future.exception():
                    status = "failed"
                else:
                    status = "done"
                self.application.setvar(group, task_name + "_status", status)
                self.application.window.update()

            # If the result should be written to the gui, do so
            answer = future.result()
            if write_result:
                self.application.setvar(group, name, answer)
                logging.debug("Set variable " + group + "." + name + " to " + str(answer))
            self.application.window.update()

        return _process_calback

    def _process_queued_tasks(self):
        """Process the tasks in the queue and adds a callback function to the future.
        This function is run in a separate thread."""
 
        with ThreadPoolExecutor() as executor:
            while True:
                # Remove the futures that are done
                self.running_tasks = [task for task in self.running_tasks if not task.done()]
                logging.debug("There are " + str(len(self.running_tasks)) + " running tasks and " + str(self.tasks.qsize()) + " tasks in the queue")

                try:
                    # Get the task from the queue. If the queue is empty, wait for 1 second  
                    task, args, task_name, write_result, group, name, wait_for_complete = self.tasks.get(
                        timeout=1
                    )
                # If the queue is empty, check if the executor is or should be shutting down
                except queue.Empty:
                    # If the executor is shutting down, or if it has run at least something, it is 
                    # not running anything anymore and the queue is empty, stop the thread
                    if self.has_run and not self.running_tasks:
                        break
                    else:                      
                        continue

                # Execute the task
                logging.debug("Executing task " + task_name)
                future = executor.submit(task, *args)
                self.application.setvar(group, task_name + "_status", "running")
                future.add_done_callback(
                    self._make_callback(task_name, write_result, group, name)
                )
                self.running_tasks.append(future)

                # Set has_run to True if it hasn't been set yet. It doesn't matter that the task 
                # is not finished since this is only used to clean up the executor and the worker 
                # thread, which only happens if the queue is empty and nothing is running
                if not self.has_run:
                    self.has_run = True

                # If wait_for_complete is True, wait for the task to complete before continueing. 
                # The user can still add new tasks since these will be added to the queue
                if wait_for_complete:
                    wait([future])

        logging.debug("Removing singleton instance")
        type(self)._instances.pop(type(self), None)
        logging.debug("Stopping worker thread")