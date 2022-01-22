import os
import errno
import numpy as np
import pandas as pd

from isochrones import get_ichrone
from isochrones.priors import ChabrierPrior


OUTPUTPATH = 'sim_gc_csv/'


def create_dir(dir_name: str):
    """ Create directory with a name 'dir_name' """
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def calc_Mv(Lv):
    """ convert Lv to Mv in the unit of L_sun"""
    Mv_sun = 4.83
    return Mv_sun - 2.5 * np.log10(Lv)


def calc_Lv(Mv):
    """ convert Mv to Lv in the unit of L_sun"""
    Mv_sun = 4.83
    return 10**(0.4*(Mv_sun - Mv))


def calc_M_abs(m, dist):
    return m - 5. * np.log10(dist / 10.)


def simulate_isochrone_gc(nstar: int, feh: float, age: float, dist: float):
    """
    Use the 'isochrones' module to simulate a globular cluster along with
    its isochrone (some stars in the prior will be gone after evaluation).

    : nstar : total number of star for the sample prior
    : feh : metalicity [Fe/H]
    : age : age of the globular cluster [log10(yr)]
    : dist : distance of the globular cluster [pc]
    : return : a data frame of the stars info in the globular gluster
    """
    tracks = get_ichrone('mist', tracks=True, bands=['V', 'G', 'BP', 'RP'])
    masses = ChabrierPrior().sample(nstar)
    df = tracks.generate(masses, age, feh, distance=dist)
    df = df.dropna()
    df['V_abs_mag'] = calc_M_abs(df['V_mag'], dist)
    df['Lv_abs'] = calc_Lv(df['V_abs_mag'])
    df['G_abs_mag'] = calc_M_abs(df['G_mag'], dist)
    return df


def csv_gc_detail(nstar, feh, age, dist):
    print('\n--------------------------------------------------\n')
    print('initial number of stars Ni = %d ' % nstar)
    df = simulate_isochrone_gc(nstar, feh, age, dist)
    print('final number of stars Nf = %d \n' % len(df))

    Lv_tot = np.sum(df['Lv_abs'])
    Mv_tot = calc_Mv(Lv_tot)
    Mass_tot = np.sum(df['mass'])
    print('GC: Mv = %0.2f mag' % Mv_tot)
    print('GC: Lv = %0.2e Lsun' % Lv_tot)
    print('GC: Mass = %.2e Msun\n' % Mass_tot)

    fname = 'Mv%0.2f_Lv%0.2e_Mass%.2e_Ni%d_Nf%d' % (Mv_tot, Lv_tot, Mass_tot, nstar, len(df))
    df.to_csv(OUTPUTPATH + fname, index=False)
    print('Done saving the csv')
    print('\n--------------------------------------------------\n')



if __name__ == '__main__':

    ngc_tot = 5    # total number of simulated GCs

    create_dir(OUTPUTPATH)

    feh = -2    # log10(z / zsun) = 1e-3
    age = np.log10(12e9)    # 12 Gyr
    dist = 1e3    # 1 kpc

    nstars = np.logspace(2., 6., num=ngc_tot)

    for nstar in nstars:
        nstar = int(nstar)
        csv_gc_detail(nstar, feh, age, dist)



    # maskobs = (17 < df['G_mag']) & (df['G_mag'] < 21)
    # print('\n%d stars detected in GAIA' % sum(maskobs))
    #
    # dist = 147 * 1e3
    # Gabsmin = calc_M_abs(17, dist)
    # Gabsmax = calc_M_abs(21, dist)
    #
    # maskobs = (Gabsmin < df['G_abs_mag']) & (df['G_abs_mag'] < Gabsmax)
    # print('\n%d stars detected in GAIA' % sum(maskobs))
