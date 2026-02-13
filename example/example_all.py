import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pylab as plt
from scipy.signal import periodogram
from roadprofile import RoadProfile, FilteredRoadProfile, DynamicRoadProfile


def example_basic():
    """Basic RoadProfile usage"""
    print("=== Basic RoadProfile ===")
    rp = RoadProfile()
    rp.set_profile_class("A")
    profile = rp.generate(L=100, dx=0.1)
    print(f"Generated {len(profile.profile)} points")
    print(f"Profile class A: {profile.profile[:5]}")
    
    rp.set_profile_class("E")
    profile = rp.generate(L=100, dx=0.1)
    print(f"Profile class E: {profile.profile[:5]}")


def example_filtered():
    """FilteredRoadProfile with time-domain filtering"""
    print("\n=== FilteredRoadProfile ===")
    frp = FilteredRoadProfile(fc=4.5, order=4)
    frp.set_profile_class("A")
    profile = frp.generate(L=100, dx=0.1)
    print(f"Filtered (fc=4.5): {profile.profile[:5]}")
    
    frp.set_profile_class("C")
    profile = frp.generate(L=100, dx=0.1)
    print(f"Filtered class C: {profile.profile[:5]}")


def example_dynamic():
    """DynamicRoadProfile with varying classes"""
    print("\n=== DynamicRoadProfile - Batch ===")
    drp = DynamicRoadProfile()
    classes = ["A"] * 50 + ["B"] * 50 + ["C"] * 50
    profile = drp.generate(L=15, dx=0.1, profile_classes=classes)
    print(f"Varying classes: {profile.profile[:5]} ... {profile.profile[45:55]} ... {profile.profile[-5:]}")


def example_generator():
    """DynamicRoadProfile real-time generator"""
    print("\n=== DynamicRoadProfile - Generator ===")
    drp = DynamicRoadProfile()
    gen = drp.create_generator(dx=0.1)
    
    print(f"Default (A): {next(gen)}")
    print(f"Default (A): {next(gen)}")
    
    gen.send('B')
    print(f"After send('B'): {next(gen)}")
    
    gen.send(0.05)
    print(f"After send(0.05): {next(gen)}")
    
    gen.send(('C', 0.2))
    print(f"After send(('C', 0.2)): {next(gen)}")


def example_irregular():
    """Irregular spacing"""
    print("\n=== Irregular Spacing ===")
    rp = RoadProfile()
    rp.set_profile_class("A")
    
    x = np.array([0, 0.05, 0.15, 0.3, 0.5, 0.8, 1.2, 1.5, 2.0])
    profile = rp.generate_at_x(x)
    print(f"x: {profile.x}")
    print(f"profile: {profile.profile}")


def example_psd_plot():
    """Generate PSD comparison plot"""
    print("\n=== Generating PSD plot ===")
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
        iso_psd = rp.Gdn0 * (n / rp.n0) ** (-rp.w)
        ax.loglog(n, iso_psd, 'r--', label='ISO Standard')

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
    print("Saved to iso_comparison.png")


if __name__ == '__main__':
    example_basic()
    example_filtered()
    example_dynamic()
    example_generator()
    example_irregular()
    
    print("\n=== Generating PSD plot (this may take a while) ===")
    example_psd_plot()
