'''
    defines a Timer class for measuring program running times.
'''

__author__ = ('Tom Streubel', 'Christian Strohm') # alphabetical order of surnames
__credits__ = ('Andreas Griewank', 'Richard Hasenfelder',
               'Oliver Kunst', 'Lutz Lehmann',
               'Manuel Radons', 'Philpp Trunschke') # alphabetical order of surnames


'''
    imports
    =======
'''
import time
from typing import Optional


class Timer(object):
    '''
        a less accurate but still useful (and especially comfortable) way to measure computation times in python
    '''
    longer_template = "Elapsed ({:>4}): {:0>2}-{:0>2}-{:0>2} : {:0>3}-{:07.3f}"
    long_template = "Elapsed ({:>4}): {:0>2}-{:0>2}-{:0>2} : {:07.3f}"
    short_template = "Elapsed ({:>4}): {:0>2}-{:0>2}-{:06.3f}"

    def __init__(self,
                 name : Optional[str] = None,
                 use_time : Optional[bool] = True, use_clock : Optional[bool] = True,
                 display_milli_secs : Optional[bool] = False, display_micro_secs : Optional[bool] = False,
                 silent_mode : Optional[bool] = False):
        self.name = name

        self.use_time = use_time
        self.use_clock = use_clock

        if display_micro_secs:
            self.milli_secs = True
        else:
            self.milli_secs = display_milli_secs
        self.micro_secs = display_micro_secs

        self.time_msg = None
        self.clock_msg = None

        self.silent_mode = silent_mode

    def _print(self, *args, **kwargs):
        if not self.silent_mode:
            print(*args, **kwargs)

    def __enter__(self):
        self.t_clock_start, self.t_time_start = time.process_time(), time.time()
        return self

    def _transformation(self, start, stop):
        hours, rem = divmod(stop - start, 3600)
        minutes, seconds = divmod(rem, 60)

        milli_secs = None
        micro_secs = None

        if self.milli_secs:
            seconds, milli_secs = divmod(seconds*1000, 1000)

        if self.micro_secs:
            milli_secs, micro_secs = divmod(milli_secs*1000, 1000)

        return hours, minutes, seconds, milli_secs, micro_secs

    def __exit__(self, exc_type : Optional = None, exc_value : Optional = None, traceback : Optional = None):
        hours_t, minutes_t, seconds_t, milli_secs_t, micro_secs_t = None, None, None, None, None
        hours_c, minutes_c, seconds_c, milli_secs_c, micro_secs_c = None, None, None, None, None

        if self.use_time:
            self.t_time_end = time.time()
            hours_t, minutes_t, seconds_t, milli_secs_t, micro_secs_t = self._transformation(self.t_time_start,
                                                                                             self.t_time_end)

        if self.use_clock:
            self.t_clock_end = time.process_time()
            hours_c, minutes_c, seconds_c, milli_secs_c, micro_secs_c = self._transformation(self.t_clock_start,
                                                                                             self.t_clock_end)

        if self.name:
            self._print('\n' + '{}'.format(self.name))
        else:
            self._print("")

        if self.use_time:
            if self.milli_secs:
                if self.micro_secs:
                    self.time_msg = Timer.longer_template.format("time",
                                                                 int(hours_t), int(minutes_t),
                                                                 int(seconds_t), int(milli_secs_t),
                                                                 micro_secs_t)
                    self._print(self.time_msg)
                else:
                    self.time_msg = Timer.long_template.format("time",
                                                               int(hours_t), int(minutes_t),
                                                               int(seconds_t), milli_secs_t)
                    self._print(self.time_msg)
            else:
                self.time_msg = Timer.short_template.format("time", int(hours_t), int(minutes_t), seconds_t)
                self._print(self.time_msg)

        if self.use_clock:
            if self.milli_secs:
                if self.micro_secs:
                    self.clock_msg = Timer.longer_template.format("proc",
                                                                  int(hours_c), int(minutes_c),
                                                                  int(seconds_c), int(milli_secs_c),
                                                                  micro_secs_c)
                    self._print(self.clock_msg)
                else:
                    self.clock_msg = Timer.long_template.format("proc",
                                                                int(hours_c), int(minutes_c),
                                                                int(seconds_c), milli_secs_c)
                    self._print(self.clock_msg)
            else:
                self.clock_msg = Timer.short_template.format("proc", int(hours_c), int(minutes_c), seconds_c)
                self._print(self.clock_msg)

        self._print("")

    def __repr__(self):
        out = 'Timer object'
        if self.name: out += f' ({self.name})'

        return out

    def __str__(self): return self.__repr__()


if __name__ == "__main__":
    t_inst = Timer('test', silent_mode = False)
    t_inst.__enter__()

    t_inst.__exit__()
    print(f"manually printed: {t_inst.time_msg} of {t_inst.name}")


    t_inst2 = Timer('test2', silent_mode = True)
    t_inst2.__enter__()
    t_inst2.__exit__()
    print(f"manually printed: {t_inst2.time_msg} of {t_inst2.name}")


    with Timer('test3') as t_inst3:
        out = 0
        for i in range(5000000):
            out += i
            out /= 2.0
    print(f"result of out: {out}; times measured by {t_inst3}")


    print('script finished.')
