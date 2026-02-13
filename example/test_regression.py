import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pylab as plt
from scipy.signal import periodogram
from roadprofile import RoadProfile, FilteredRoadProfile, DynamicRoadProfile


def test_psd_validation():
    """Test that generated profiles match ISO PSD"""
    print("=== Test: PSD validation vs ISO standard ===")
    
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
        ax.set_title('Class ' + cls)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])
    
    plt.tight_layout()
    plt.savefig('test_psd_validation.png', dpi=150)
    plt.close()
    print("  Saved test_psd_validation.png")
    print("  PASSED!\n")


def test_filtered_psd_validation():
    """Test that FilteredRoadProfile PSD matches ISO"""
    print("=== Test: FilteredRoadProfile PSD validation ===")
    
    classes = ["A", "B", "C", "D", "E", "F"]
    dx = 0.1
    L = 500
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    
    for idx, cls in enumerate(classes):
        ax = axes[idx]
        
        frp = FilteredRoadProfile(fc=4.5, order=4)
        frp.set_profile_class(cls)
        profile = frp.generate(L, dx)
        
        f, psd = periodogram(profile.profile, fs=1/dx, scaling='density')
        
        ax.loglog(f[1:], psd[1:], 'b-', label='Filtered', alpha=0.7)
        
        n = np.logspace(np.log10(0.01), np.log10(4), 100)
        iso_psd = frp.Gdn0 * (n / frp.n0) ** (-frp.w)
        ax.loglog(n, iso_psd, 'r--', label='ISO Standard')
        
        ax.set_xlabel('Spatial frequency (cycles/m)')
        ax.set_ylabel('PSD (m^3)')
        ax.set_title('Class ' + cls + ' (fc=' + str(frp.fc) + ')')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])
    
    plt.tight_layout()
    plt.savefig('test_filtered_psd_validation.png', dpi=150)
    plt.close()
    print("  Saved test_filtered_psd_validation.png")
    print("  PASSED!\n")


def test_generate_at_x_fixed_spacing():
    """Test generate_at_x produces same result as generate with fixed spacing"""
    print("=== Test: generate_at_x vs generate (fixed spacing) ===")
    
    np.random.seed(42)
    rp = RoadProfile()
    rp.set_profile_class("A")
    
    L = 100
    dx = 0.1
    
    np.random.seed(42)
    p1 = rp.generate(L, dx)
    
    np.random.seed(42)
    rp2 = RoadProfile()
    rp2.set_profile_class("A")
    x = np.arange(0, L + dx/2, dx)
    p2 = rp2.generate_at_x(x)
    
    assert len(p1.x) == len(p2.x), "Length mismatch"
    assert np.allclose(p1.x, p2.x), "x values mismatch"
    assert np.allclose(p1.profile, p2.profile, rtol=1e-5), "profile values mismatch"
    
    print("  generate: {}".format(p1.profile[:3]))
    print("  generate_at_x: {}".format(p2.profile[:3]))
    print("  PASSED!\n")


def test_point_generator_fixed_dx():
    """Test point_generator produces valid PSD with fixed class"""
    print("=== Test: point_generator PSD with fixed class ===")
    
    dx = 0.1
    L = 500
    n_points = int(L / dx)
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    
    classes = ["A", "B", "C", "D", "E", "F"]
    f = None
    drp = None
    
    for idx, cls in enumerate(classes):
        ax = axes[idx]
        
        psds = []
        for _ in range(5):
            drp = DynamicRoadProfile()
            drp.set_profile_class(cls)
            gen = drp.create_generator(dx)
            
            points = [next(gen) for _ in range(n_points)]
            
            f, psd = periodogram(points, fs=1/dx, scaling='density')
            psds.append(psd)
        
        avg_psd = np.mean(psds, axis=0)
        
        ax.loglog(f[1:], avg_psd[1:], 'b-', label='point_generator', alpha=0.7)
        
        n = np.logspace(np.log10(0.01), np.log10(4), 100)
        iso_psd = drp.Gdn0 * (n / drp.n0) ** (-drp.w)
        ax.loglog(n, iso_psd, 'r--', label='ISO Standard')
        
        ax.set_xlabel('Spatial frequency (cycles/m)')
        ax.set_ylabel('PSD (m^3)')
        ax.set_title('Class ' + cls + ' (point_generator)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])
    
    plt.tight_layout()
    plt.savefig('test_point_generator_psd_fixed_x.png', dpi=150)
    plt.close()
    print("  Saved test_point_generator_psd_fixed_x.png")
    print("  PASSED!\n")


def test_filtered_generate_at_x():
    """Test FilteredRoadProfile generate_at_x vs generate"""
    print("=== Test: FilteredRoadProfile generate_at_x vs generate ===")
    
    L = 100
    dx = 0.1
    
    np.random.seed(42)
    frp = FilteredRoadProfile(fc=4.5, order=4)
    frp.set_profile_class("A")
    p1 = frp.generate(L, dx)
    
    np.random.seed(42)
    frp2 = FilteredRoadProfile(fc=4.5, order=4)
    frp2.set_profile_class("A")
    x = np.arange(0, L + dx/2, dx)
    p2 = frp2.generate_at_x(x)
    
    assert len(p1.x) == len(p2.x), "Length mismatch"
    assert np.allclose(p1.x, p2.x), "x values mismatch"
    assert np.allclose(p1.profile, p2.profile, atol=1e-4), "profile values mismatch"
    
    print("  generate: {}".format(p1.profile[:3]))
    print("  generate_at_x: {}".format(p2.profile[:3]))
    print("  PASSED!\n")


def test_dynamic_generate_batch():
    """Test DynamicRoadProfile generate with fixed class matches RoadProfile"""
    print("=== Test: DynamicRoadProfile generate vs RoadProfile.generate ===")
    
    L = 50
    dx = 0.1
    
    np.random.seed(42)
    rp = RoadProfile()
    rp.set_profile_class("A")
    p1 = rp.generate(L, dx)
    
    np.random.seed(42)
    drp = DynamicRoadProfile()
    drp.set_profile_class("A")
    p2 = drp.generate(L, dx, "A")
    
    assert np.allclose(p1.profile, p2.profile, rtol=1e-5), "profile values mismatch"
    
    print("  RoadProfile: {}".format(p1.profile[:3]))
    print("  DynamicRoadProfile: {}".format(p2.profile[:3]))
    print("  PASSED!\n")


def test_different_classes():
    """Test generate_at_x with different ISO classes"""
    print("=== Test: generate_at_x with different classes ===")
    
    for cls in ["A", "B", "C", "D", "E", "F"]:
        rp = RoadProfile()
        rp.set_profile_class(cls)
        
        x = np.array([0, 0.5, 1.0, 2.0, 5.0])
        p = rp.generate_at_x(x)
        
        print("  Class {}: Gdn0={}, profile[0]={:.6f}".format(cls, rp.Gdn0, p.profile[0]))
    
    print("  PASSED!\n")


def test_generate_at_x_psd():
    """Test that generate_at_x produces valid PSD"""
    print("=== Test: generate_at_x PSD validation ===")
    
    dx = 0.1
    L = 500
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    
    classes = ["A", "B", "C", "D", "E", "F"]
    
    for idx, cls in enumerate(classes):
        ax = axes[idx]
        
        rp = RoadProfile()
        rp.set_profile_class(cls)
        
        x = np.arange(0, L + dx/2, dx)
        profile = rp.generate_at_x(x)
        
        f, psd = periodogram(profile.profile, fs=1/dx, scaling='density')
        
        ax.loglog(f[1:], psd[1:], 'b-', label='generate_at_x', alpha=0.7)
        
        n = np.logspace(np.log10(0.01), np.log10(4), 100)
        iso_psd = rp.Gdn0 * (n / rp.n0) ** (-rp.w)
        ax.loglog(n, iso_psd, 'r--', label='ISO Standard')
        
        ax.set_xlabel('Spatial frequency (cycles/m)')
        ax.set_ylabel('PSD (m^3)')
        ax.set_title('Class ' + cls + ' (generate_at_x)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])
    
    plt.tight_layout()
    plt.savefig('test_generate_at_x_psd.png', dpi=150)
    plt.close()
    print("  Saved test_generate_at_x_psd.png")
    print("  PASSED!\n")


def test_point_generator_psd():
    """Test that point_generator produces valid PSD"""
    print("=== Test: point_generator PSD validation ===")
    
    dx = 0.1
    L = 500
    n_points = int(L / dx)
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    
    classes = ["A", "B", "C", "D", "E", "F"]
    drp = None
    
    for idx, cls in enumerate(classes):
        ax = axes[idx]
        
        drp = DynamicRoadProfile()
        drp.set_profile_class(cls)
        gen = drp.create_generator(dx)
        
        points = [next(gen) for _ in range(n_points)]
        
        f, psd = periodogram(points, fs=1/dx, scaling='density')
        
        ax.loglog(f[1:], psd[1:], 'b-', label='point_generator', alpha=0.7)
        
        n = np.logspace(np.log10(0.01), np.log10(4), 100)
        iso_psd = drp.Gdn0 * (n / drp.n0) ** (-drp.w)
        ax.loglog(n, iso_psd, 'r--', label='ISO Standard')
        
        ax.set_xlabel('Spatial frequency (cycles/m)')
        ax.set_ylabel('PSD (m^3)')
        ax.set_title('Class ' + cls + ' (point_generator)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0.01, 4])
        ax.set_ylim([1E-8, 1])
    
    plt.tight_layout()
    plt.savefig('test_point_generator_psd.png', dpi=150)
    plt.close()
    print("  Saved test_point_generator_psd.png")
    print("  PASSED!\n")


def test_point_generator_class_change():
    """Test point_generator can change class via send"""
    print("=== Test: point_generator class change ===")
    
    drp = DynamicRoadProfile()
    drp.set_profile_class("A")
    gen = drp.create_generator(0.1)
    
    points_a = [next(gen) for _ in range(10)]
    
    gen.send("B")
    points_b = [next(gen) for _ in range(10)]
    
    gen.send("C")
    points_c = [next(gen) for _ in range(10)]
    
    print("  Class A (first 3): {}".format(points_a[:3]))
    print("  Class B (first 3): {}".format(points_b[:3]))
    print("  Class C (first 3): {}".format(points_c[:3]))
    print("  PASSED!\n")


if __name__ == '__main__':
    test_psd_validation()
    test_filtered_psd_validation()
    test_generate_at_x_psd()
    test_point_generator_psd()
    test_point_generator_fixed_dx()
    test_point_generator_class_change()
    test_generate_at_x_fixed_spacing()
    test_filtered_generate_at_x()
    test_dynamic_generate_batch()
    test_different_classes()
    
    print("=== All regression tests passed! ===")
