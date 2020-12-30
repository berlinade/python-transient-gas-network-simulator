'''
    imports
'''
import numpy as np
from paso.solvers.dae.ImpEuler import integrate, ImpEuler_integration_options
from ad.timer import Timer

from paso.systems_of_euqations.dae.sin_minus_sin.sources import f, sol, v0 as x0, t0, T


if __name__ == "__main__":
    h = 0.05

    with Timer():
        integrator_opts = ImpEuler_integration_options()
        integrator_opts.cycADa = True

        print(integrator_opts)

        ImpEuler_report = integrate(f, x0, t0 = t0, T = T, h = h,
                                  integrator_opts = integrator_opts)

    print('save solution')
    np.save('results_dump/Ts_ImpEuler_sin_minus_sin', ImpEuler_report.Ts)
    np.save('results_dump/Xs_ImpEuler_sin_minus_sin', ImpEuler_report.Xs)
    print('saving completed')


    print('script finished.')
