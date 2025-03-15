

import gc                              # Memory allocation garbage collector
import utime                           # Micropython version of time library
import micropython                     # This shuts up incorrect warnings

class Task:
    def __init__(self, run_fun, name="NoName", priority=0, period=None,
                 profile=False, trace=False, shares=()):
        if shares:
            self._run_gen = run_fun(shares)
        else:
            self._run_gen = run_fun()

        ## The name of the task, hopefully a short and descriptive string.
        self.name = name
 
        self.priority = int(priority)

        if period != None:
            self.period = int(period * 1000)
            self._next_run = utime.ticks_us() + self.period
        else:
            self.period = period
            self._next_run = None


        self._prof = profile
        self.reset_profile()

        self._prev_state = 0

        self._trace = trace
        self._tr_data = []
        self._prev_time = utime.ticks_us()

        ## Flag which is set true when the task is ready to be run by the
        #  scheduler
        self.go_flag = False

    def schedule(self) -> bool:
        if self.ready():
            self.go_flag = False

            if self._prof:
                stime = utime.ticks_us()

            curr_state = next(self._run_gen)

            if self._prof or self._trace:
                etime = utime.ticks_us()

            # If profiling, save timing data
            if self._prof:
                self._runs += 1
                runt = utime.ticks_diff(etime, stime)
                if self._runs > 2:
                    self._run_sum += runt
                    if runt > self._slowest:
                        self._slowest = runt
            if self._trace:
                try:
                    if curr_state != self._prev_state:
                        self._tr_data.append(
                            (utime.ticks_diff(etime, self._prev_time),
                             curr_state))
                except MemoryError:
                    self._trace = False
                    gc.collect()

                self._prev_state = curr_state
                self._prev_time = etime

            return True

        else:
            return False

    @micropython.native
    def ready(self) -> bool:
        if self.period != None:
            late = utime.ticks_diff(utime.ticks_us(), self._next_run)
            if late > 0:
                self.go_flag = True
                self._next_run = utime.ticks_diff(self.period, 
                                                  -self._next_run)

                # If keeping a latency profile, record the data
                if self._prof:
                    self._late_sum += late
                    if late > self._latest:
                        self._latest = late
        return self.go_flag
    def set_period(self, new_period):
        if new_period is None:
            self.period = None
        else:
            self.period = int(new_period) * 1000
    def reset_profile(self):
        self._runs = 0
        self._run_sum = 0
        self._slowest = 0
        self._late_sum = 0
        self._latest = 0
    def get_trace(self):
        tr_str = 'Task ' + self.name + ':'
        if self._trace:
            tr_str += '\n'
            last_state = 0
            total_time = 0.0
            for item in self._tr_data:
                total_time += item[0] / 1000000.0
                tr_str += '{: 12.6f}: {: 2d} -> {:d}\n'.format (total_time, 
                    last_state, item[1])
                last_state = item[1]
        else:
            tr_str += ' not traced'
        return tr_str
    def go(self):
        self.go_flag = True
    def __repr__(self):
        rst = f"{self.name:<16s}{self.priority: 4d}"
        try:
            rst += f"{(self.period / 1000.0): 10.1f}"
        except TypeError:
            rst += '         -'
        rst += f"{self._runs: 8d}"

        if self._prof and self._runs > 0:
            avg_dur = (self._run_sum / self._runs) / 1000.0
            avg_late = (self._late_sum / self._runs) / 1000.0
            rst += f"{avg_dur: 10.3f}{(self._slowest / 1000.0): 10.3f}"
            if self.period != None:
                rst += f"{avg_late: 10.3f}{(self._latest / 1000.0): 10.3f}"
        return rst

class TaskList:
    def __init__(self):
        self.pri_list = []

    def append(self, task):
        # See if there's a tasklist with the given priority in the main list
        new_pri = task.priority
        for pri in self.pri_list:
            # If a tasklist with this priority exists, add this task to it.
            if pri[0] == new_pri:
                pri.append(task)
                break
        else:
            self.pri_list.append([new_pri, 2, task])

        # Make sure the main list (of lists at each priority) is sorted
        self.pri_list.sort(key=lambda pri: pri[0], reverse=True)
    @micropython.native
    def rr_sched(self):
        # For each priority level, run all tasks at that level
        for pri in self.pri_list:
            for task in pri[2:]:
                task.schedule()

    @micropython.native
    def pri_sched(self):
        for pri in self.pri_list:
            tries = 2
            length = len(pri)
            while tries < length:
                ran = pri[pri[1]].schedule()
                tries += 1
                pri[1] += 1
                if pri[1] >= length:
                    pri[1] = 2
                if ran:
                    return

    def __repr__(self):
        ret_str = 'TASK             PRI    PERIOD    RUNS   AVG DUR   MAX ' \
            'DUR  AVG LATE  MAX LATE\n'
        for pri in self.pri_list:
            for task in pri[2:]:
                ret_str += str(task) + '\n'

        return ret_str

task_list = TaskList()