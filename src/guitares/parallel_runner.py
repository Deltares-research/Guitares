from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
import traceback
import re

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    # result = pyqtSignal(object)
    # progress = pyqtSignal(int)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, runner):
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = runner.button.element.callback
        self.args = runner.button
        self.done_fn = runner._set_done
        self.signals = WorkerSignals()

    def run(self):
        '''
        Run the runner function with passed args. If the runner function returns
        a value, ignore this.
        '''
        _ = self.fn(self.args)
        self.signals.finished.emit()
        

class ParallelRunner:
    """
    
    """
    def __init__(self, button) -> None:

        self.button = button
        self.worker = Worker(self)
        self.worker.signals.finished.connect(self._set_done)

    def parallel_callback_wrapper(self):
        try:
            status = self.button.element.getvar(self.button.element.variable_group, self.button.element.parallelization['variable'])
            if status and "Running" in status:
                num = ParallelRunner._find_running_instances(status)[-1]
            else:
                num = 0
            
            print(f"Setting status of {self.button.element.parallelization['variable']} to Running {num + 1}")
            self.button.element.setvar(self.button.element.variable_group, self.button.element.parallelization['variable'], "Running " + str(num + 1))
            self.button.element.threadpool.start(self.worker)
            self.button.element.window.update()
        except:
            traceback.print_exc()

    @staticmethod
    def _find_running_instances(text):
        pattern = r"Running (\d+)"
        matches = re.findall(pattern, text)
        return [int(match) for match in matches]

    def _set_done(self):        
        status = self.button.element.getvar(self.button.element.variable_group, self.button.element.parallelization['variable'])
        print(f"Done, {self.button.element.parallelization['variable']} was {status}")
        if "Running" in status:
            num = self._find_running_instances(status)[-1]
            if num == 1:
                self.button.element.setvar(self.button.element.variable_group, self.button.element.parallelization['variable'], "Done")
                print("Setting status to Done")
                self.button.element.window.update()
            else:
                self.button.element.setvar(self.button.element.variable_group, self.button.element.parallelization['variable'], "Running " + str(num - 1))
                print("Setting status to Running " + str(num - 1))
                self.button.element.window.update()
