import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pylab as plt
from scipy.signal import periodogram
from roadprofile import RoadProfile, FilteredRoadProfile


def iso_psd(n, Gdn0, n0=0.1, w=2):
    return Gdn0 * (n / n0) ** (-w)


def main():
    classes = ["A", "B", "C", "D", "E", "F"]
    dx = 0.1
    L = 500

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for idx, cls in enumerate(classes):
        ax = axes[idx]

        rp = RoadProfile()
        rp.set_profile_class(cls)
        profile = rp.generate(L, dx)

        f, psd = periodogram(profile.profile, fs=1/dx, scaling='density')

        ax.loglog(f[1:], psd[1:], 'b-', label='Generated', alpha=0.7)

        n = np.logspace(np.log10(0.01), np.log10(4), 100)
        ax.loglog(n, iso_psd(n, rp.Gdn0), 'r--', label='ISO Standard')

        ax.set_xlabel('Spatial frequency (cycles/m)')
        ax.set_ylabel('PSD (m^3)')
        ax.set_title(f'Class {cls}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])

    plt.tight_layout()
    plt.savefig('iso_comparison.png', dpi=150)
    plt.show()

    print("FilteredRoadProfile comparison:")
    fig2, axes2 = plt.subplots(2, 3, figsize=(12, 8))
    axes2 = axes2.flatten()

    for idx, cls in enumerate(classes):
        ax = axes2[idx]

        frp = FilteredRoadProfile()
        frp.set_profile_class(cls)
        profile = frp.generate(L, dx)

        f, psd = periodogram(profile.profile, fs=1/dx, scaling='density')

        ax.loglog(f[1:], psd[1:], 'b-', label='Filtered', alpha=0.7)

        n = np.logspace(np.log10(0.01), np.log10(4), 100)
        ax.loglog(n, iso_psd(n, frp.Gdn0), 'r--', label='ISO Standard')

        ax.set_xlabel('Spatial frequency (cycles/m)')
        ax.set_ylabel('PSD (m^3)')
        ax.set_title(f'Class {cls} (fc={frp.fc}, order={frp.order})')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])

    plt.tight_layout()
    plt.savefig('filtered_comparison.png', dpi=150)
    plt.show()


if __name__ == '__main__':
    main()
