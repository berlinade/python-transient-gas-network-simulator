'''
    realizes different types unary (1D in the domain) interpolation of data tables. types are:
     - linear
     - piecewise constant
     - 'principally' piecewise constant but with relatively short continuous transitions between plateus
'''

__author__ = ('Tom Streubel',)  # alphabetical order of surnames
__credits__ = tuple()  # alphabetical order of surnames

'''
    imports
    =======
'''
import numpy as np
from simulator.resources.units import second, minute
from simulator.resources.auxiliary import ModellingError
from typing import Union, List, Tuple, Optional


class table_lookup(object):

    def __init__(self,
                 timepoints : Union[List[float], Tuple[float, ...], np.ndarray],
                 functionValues : Union[List[float], Tuple[float, ...], np.ndarray],
                 mode : Optional[str] = "pl", smoothing_offset : Optional[float] = 3.0*minute,
                 horizon : Optional[Tuple[float, float]] = (0.0*minute, 0.0*minute),
                 t_horizon_debug : Optional[float] = None):
        '''
            :param timepoints:
            :param functionValues:
            :param mode:
            :param smoothing_offset:
            :param horizon:
            :param t_horizon_debug:
        '''

        ''' parse, check & sort timepoints, functionvalues '''
        if (len(timepoints) < 1) or (len(timepoints) != len(functionValues)):
            raise ModellingError("len(timepoints) > 0 and len(timepoints) == len(functionValues)!")
        timepoints, functionValues = zip(*sorted(zip(timepoints, functionValues)))
        self.Ts = np.array(timepoints, copy = False)
        self.FTs = np.array(functionValues, copy = False)

        ''' parse mode '''
        if not (mode.lower() in ["piecewise constant", "pc", "interpolate", "lin", "pl", "piecewise linear"]):
            raise ModellingError("mode has to be from ['piecewise constant', 'interpolate']!")
        else:
            if mode.lower() in ["piecewise constant", "pc"]:
                self.mode = "pc"
            else:
                self.mode = "lin"

        ''' if mode = pc (i.e. picewise constant) parse and check smothening_offset, which is used to avoid discontinuous jumps '''
        self.offset = smoothing_offset
        if self.mode == "pc":
            if self.offset is None:
                self.offset = 0.0
            if self.offset < 0.0:
                raise ModellingError("smoothing offset cannot be negative (if you are using mode = 'pc')!")
            if self.offset > 0.0:
                ''' in case of smoothing compute additional timepoints and copy functionvalues '''
                new_Ts = [self.Ts[0]]
                new_FTs = [self.FTs[0]]

                tj = self.Ts[0]
                FTj = self.FTs[0]
                for ti, FTi in zip(self.Ts[1:], self.FTs[1:]):
                    if  tj < ti - self.offset:
                        new_Ts.extend([ti - self.offset, ti])
                        new_FTs.extend([FTj, FTi])
                    else:
                        new_Ts.append(ti)
                        new_FTs.append(FTi)
                    tj = ti
                    FTj = FTi

                self.Ts = np.array(new_Ts)
                self.FTs = np.array(new_FTs)
        else:
            self.offset = None

        if not ((self.mode == "pc") and (self.offset == 0.0)):
            if (horizon[0] > 0.0) or (horizon[1] < 0.0):
                raise ModellingError("first horizon boundary has to be non positive and the other non negative!")
            self.horizon = horizon
            self.horizon_diameter = horizon[1] - horizon[0]

            ''' compute slopes in case of non-zero horizon '''
            self.slopes = np.zeros(shape = (len(self.Ts) + 1,))
            for i in range(1, len(self.Ts)):
                self.slopes[i] = (self.FTs[i] - self.FTs[i - 1])/(self.Ts[i] - self.Ts[i-1])
        else:
            self.horizon_diameter = 0.0

        if self.horizon_diameter == 0.0:
            self.last_t_id = 0

            self.debug_t = None
        else:
            self.last_t_horizon_back_id = 0
            self.last_t_horizon_front_id = 0

            self.debug_t = t_horizon_debug

    def _search_t_and_id(self, id_start, t):
        j, i = id_start, None
        tj, ti = self.Ts[id_start], None
        for i, ti in enumerate(self.Ts[id_start + 1:], id_start + 1):
            if t < ti:
                break
            j = i
            tj = ti

        return j, tj, i, ti

    def _closed_form_table_look_up_algorithm(self, t, timepoints, slopes, F_left, F_right):
        sim1, si = slopes[0], None
        t_delta = t - timepoints[0]
        result = (F_left + F_right) + sim1*t_delta
        for i, (si, tim1) in enumerate(zip(slopes[1:], timepoints)):
            t_delta = t - tim1
            result = result + (si - sim1)*abs(t_delta)
            sim1 = si
        return (result + si*t_delta)/2.0

    def __call__(self, t):
        if len(self.Ts) == 1:
            return self.FTs[0]

        if self.horizon_diameter == 0.0:
            if t < self.Ts[self.last_t_id]:
                if t < self.Ts[0]:
                    return self.FTs[0]

                j, tj, i, ti = self._search_t_and_id(0, t)
                self.last_t_id = i
            elif t == self.Ts[self.last_t_id]:
                return self.FTs[self.last_t_id]
            else:
                if t > self.Ts[-1]:
                    return self.FTs[-1]

                j, tj, i, ti = self._search_t_and_id(self.last_t_id, t)
                self.last_t_id = j

            if (self.mode == "lin") or (self.offset > 0.0):
                return self.FTs[j] + (t - tj)*self.slopes[i]
            return self.FTs[j]
        else:
            if self.debug_t is None:
                t_base = t
            else:
                t_base = self.debug_t

            t_back = t_base + self.horizon[0]
            if t_back < self.Ts[self.last_t_horizon_back_id]:
                if t_back < self.Ts[0]:
                    j, i = 0, 1
                else:
                    j, _, i, _ = self._search_t_and_id(0, t_back)
                self.last_t_horizon_back_id = i
            else:
                if t_back > self.Ts[-1]:
                    i = len(self.Ts) - 1
                    j = i - 1
                else:
                    j, _, i, _ = self._search_t_and_id(self.last_t_horizon_back_id, t_back)
                self.last_t_horizon_back_id = j
            id_back = j

            t_front = t_base + self.horizon[1]
            if t_front < self.Ts[self.last_t_horizon_front_id]:
                if t_front < self.Ts[0]:
                    j, i = 0, 1
                else:
                    j, _, i, _ = self._search_t_and_id(0, t_front)
                self.last_t_horizon_front_id = i
            else:
                if t_front > self.Ts[-1]:
                    i = len(self.Ts) - 1
                    j = i - 1
                else:
                    j, _, i, _ = self._search_t_and_id(self.last_t_horizon_front_id, t_front)
                self.last_t_horizon_front_id = j
            id_front = i

            return self._closed_form_table_look_up_algorithm(t,
                                                             self.Ts[id_back : id_front + 1],
                                                             self.slopes[id_back : id_front + 2],
                                                             self.FTs[id_back], self.FTs[id_front])


default_io = table_lookup([0.0], [1.0]) # i.e. will always return 1.0


if __name__ == "__main__":

    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np


    Ts = [221.03, 30.3, 44.21, 46.21, 175.0, 202.0, 108.9, 166.0]
    FTs = [2.3, -1.2, -0.2,   1.3,   -0.2,   5.3,   -1.2,  0.3]

    horizon = (-0.0, 0.0)
    t_horizon_debug = 200.0
    func0 = table_lookup(Ts, FTs,
                         mode = "pc", smoothing_offset = None, horizon = horizon,
                         t_horizon_debug = t_horizon_debug) # horizon ignored here since no smoothing
    func1 = table_lookup(Ts, FTs,
                         mode = "pc", smoothing_offset = 5.0*second, horizon = horizon,
                         t_horizon_debug = t_horizon_debug)
    func2 = table_lookup(Ts, FTs,
                         mode = "pl", smoothing_offset = 5.0*second, horizon = horizon,
                         t_horizon_debug = t_horizon_debug)

    # Data for plotting
    t = np.arange(0.0, 230.0, 0.1)
    s0 = [func0(ti) for ti in t]
    s1 = [func1(ti) for ti in t]
    s2 = [func2(ti) for ti in t]
    s3 = [default_io(ti) for ti in t]

    fig, ax = plt.subplots()
    ax.plot(t, s0, label = "piecewise constant (no transition)")
    ax.plot(t, s1, label = "piecewise constant (linear transition)")
    ax.plot(t, s2, label = "piecewise linear")
    ax.plot(t, s3, label = "default io")
    ax.plot(func1.Ts, func1.FTs, "go", label = "hidden nodes (smoothing)")
    ax.plot(Ts, FTs, "ro", label = "data points")

    ax.set(xlabel='time', ylabel='value',
           title='interpolants')
    ax.grid()

    plt.legend()
    plt.show()
