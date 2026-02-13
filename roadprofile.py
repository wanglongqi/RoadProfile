# -*- coding: utf-8 -*-
from __future__ import print_function
"""
Created on Thu Mar 02 08:45:23 2017

Visit https://github.com/wanglongqi/RoadProfile/blob/master/roadprofile.py for lastest version.

@author: Longqi WANG
"""

import numpy as np
from collections import namedtuple
from scipy.signal import butter, filtfilt
from scipy.interpolate import interp1d

Profile = namedtuple('Profile', ['x', 'profile'])


class RoadProfile(object):

    '''
    Based on method described in:
        Da Silva, J. G. S. "Dynamical performance of highway bridge
        decks with irregular pavement surface."
        Computers & structures 82.11 (2004): 871-881.

    Attributes:
        Gdn0 (float): Gd(n0)
        n0 (float): reference spatial frequency
        n_max (float): max spatial frequency
        n_min (float): min spatial frequency
        w (int): set according to the value in page 14 of ISO
    '''

    n_min = 0.0078  # min spatial frequency
    n_max = 4.0  # max spatial frequency
    n0 = 0.1  # reference spatial frequency
    w = 2  # set according to the value in page 14 of ISO
    iso_Gdn0 = {"A": 32E-6,
                "B": 128E-6,
                "C": 512E-6,
                "D": 2048E-6,
                "E": 8192E-6,
                "F": 32768E-6}

    def __init__(self, Gdn0=32E-6):
        self.Gdn0 = Gdn0

    def generate(self, L=100., dx=0.1, center=False):
        x = np.arange(0, L + dx / 2., dx)
        components = int(L / dx / 2)
        ns = np.linspace(self.n_min, self.n_max, components)

        Gd = np.sqrt(self.Gdn0 * (ns / self.n0) ** (-self.w) *
                     2 * (self.n_max - self.n_min) / components)

        profile = np.zeros(len(x))
        phase = np.random.rand(components) * 2 * np.pi
        for i in range(len(x)):
            profile[i] = np.sum(Gd * np.cos(2 * np.pi * ns * x[i] - phase))

        if center:
            profile -= np.mean(profile)

        return Profile(x=x, profile=profile)

    def set_profile_class(self, profile_class="A"):
        try:
            self.Gdn0 = self.iso_Gdn0[profile_class.upper()]
        except KeyError:
            raise ValueError("Profile name is not predefined.")

    def get_profile_by_class(self, profile_class="A", L=100, dx=0.1, center=False):
        try:
            self.Gdn0 = self.iso_Gdn0[profile_class.upper()]
            return self.generate(L, dx, center)
        except KeyError:
            raise ValueError("Profile name is not predefined.")

    def generate_at_x(self, x):
        if isinstance(x, list):
            x = np.array(x)
        
        x = np.sort(x)
        x_min = x.min()
        x_max = x.max()
        
        dx_ref = np.mean(np.diff(x))
        L = x_max - x_min
        
        result = self.generate(L, dx_ref)
        
        interp_func = interp1d(result.x, result.profile, kind='cubic', bounds_error=False, fill_value='extrapolate')
        profile = interp_func(x - x_min)

        return Profile(x=x, profile=profile)


class FilteredRoadProfile(RoadProfile):

    iso_filter_params = {
        "A": {"fc": 4.5, "order": 4},
        "B": {"fc": 4.5, "order": 4},
        "C": {"fc": 4.5, "order": 4},
        "D": {"fc": 4.5, "order": 4},
        "E": {"fc": 4.5, "order": 4},
        "F": {"fc": 4.5, "order": 4},
    }

    def __init__(self, Gdn0=32E-6, fc=1.0, order=4):
        super(FilteredRoadProfile, self).__init__(Gdn0)
        self.fc = fc
        self.order = order

    def set_filter_params(self, fc=1.0, order=4):
        self.fc = fc
        self.order = order

    def set_profile_class(self, profile_class="A"):
        super(FilteredRoadProfile, self).set_profile_class(profile_class)
        params = self.iso_filter_params[profile_class.upper()]
        self.fc = params["fc"]
        self.order = params["order"]

    def generate_at_x(self, x):
        result = super(FilteredRoadProfile, self).generate_at_x(x)
        fs = 1.0 / np.mean(np.diff(x))
        nyquist = fs / 2
        if self.fc >= nyquist:
            return result
        b, a = butter(self.order, self.fc / nyquist, btype='low')
        filtered = filtfilt(b, a, result.profile)
        return Profile(x=result.x, profile=filtered)


class DynamicRoadProfile(FilteredRoadProfile):

    def __init__(self, Gdn0=32E-6, fc=4.5, order=4):
        super(DynamicRoadProfile, self).__init__(Gdn0, fc, order)
        self._current_class = "A"
        self._segment_generator = None

    def set_profile_class(self, profile_class):
        self._current_class = profile_class.upper()
        self.Gdn0 = self.iso_Gdn0.get(self._current_class, 32E-6)

    def generate(self, L=100., dx=0.1, profile_classes="A"):
        x = np.arange(0, L + dx / 2., dx)
        n_points = len(x)

        if isinstance(profile_classes, str):
            profile_classes = [profile_classes.upper()] * n_points
        else:
            profile_classes = [c.upper() for c in profile_classes]
            if len(profile_classes) < n_points:
                profile_classes = profile_classes + [profile_classes[-1]] * (n_points - len(profile_classes))

        profile = np.zeros(n_points)
        current_cls = profile_classes[0]
        segment_start = 0

        for i in range(1, n_points + 1):
            if i == n_points or (i < n_points and profile_classes[i] != current_cls):
                segment_len = i - segment_start
                self.Gdn0 = self.iso_Gdn0[current_cls]
                result = super(DynamicRoadProfile, self).generate(segment_len * dx, dx)
                profile[segment_start:i] = result.profile[:segment_len]
                if i < n_points:
                    current_cls = profile_classes[i]
                    segment_start = i

        return Profile(x=x, profile=profile)

    def generator(self, dx=0.1):
        self._segment_generator = None
        while True:
            cls = yield
            self._current_class = cls.upper() if isinstance(cls, str) else cls

    def point_generator(self, dx=0.1):
        components = 2000
        ns = np.linspace(self.n_min, self.n_max, components)
        phase = np.random.rand(components) * 2 * np.pi
        base_Gd = np.sqrt((ns / self.n0) ** (-self.w) *
                          2 * (self.n_max - self.n_min) / components)

        x = 0.0
        current_dx = dx
        scale = np.sqrt(self.Gdn0)

        while True:
            point = np.dot(base_Gd, np.cos(2 * np.pi * ns * x - phase)) * scale

            received = yield point

            if received is not None:
                if isinstance(received, (int, float)):
                    current_dx = received
                elif isinstance(received, str):
                    gdn0 = self.iso_Gdn0.get(received.upper(), 32E-6)
                    scale = np.sqrt(gdn0)

            x += current_dx

    def create_generator(self, dx=0.1):
        gen = self.point_generator(dx)
        next(gen)
        return gen


if __name__ == '__main__':
    testprofile = RoadProfile()
    print(testprofile.generate(1, 0.1))
    testprofile.set_profile_class("E")
    print(testprofile.generate(1, 0.1))
    print(testprofile.get_profile_by_class("A", 1, 0.1))
