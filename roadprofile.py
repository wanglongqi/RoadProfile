# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 08:45:23 2017

Visit https://github.com/wanglongqi/RoadProfile/blob/master/roadprofile.py for lastest version.

@author: Longqi WANG
"""

import numpy as np


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
        '''Gdn0, displacement power spectral density (m**3)

        Args:
            Gdn0 (float, optional): Gd(n0)
        '''
        self.Gdn0 = Gdn0

    def generate(self, L=100., dx=0.1, center = False):
        """Summary

        Args:
            L (float, optional): Length of the road profile
            dx (float, optional): Interval between two points
            center (bool, optional): Center the profile mean to zero

        Returns:
            array : Road profile
        """
        x = np.arange(0, L+dx/2., dx)
        components = int(L/dx/2)
        ns = np.linspace(self.n_min, self.n_max, components)

        Gd = np.sqrt(self.Gdn0 * (ns/self.n0)**(-self.w) *
                     2*(self.n_max - self.n_min)/components)

        profile = np.zeros(np.size(x))
        phase = np.random.rand(components)*2*np.pi
        for i in range(len(x)):
            profile[i] = np.sum(Gd*np.cos(2*np.pi*ns*x[i]-phase))

        if center:
            profile -= np.mean(profile)

        return [x,profile]

    def set_profile_class(self, profile_class="A"):
        """Summary

        Args:
            profile_class (str, optional): A-F
        """
        try:
            self.Gdn0 = self.iso_Gdn0[profile_class.upper()]
        except:
            raise ValueError("Profile name is not predefined.")

    def get_profile_by_class(self, profile_class="A", L=100, dx=0.1, center = False):
        """Summary

        Args:
            profile_class (str, optional): A-F
            L (int, optional): Length of the road profile
            dx (float, optional): Interval between two points
            center (bool, optional): Center the profile mean to zero

        Returns:
            array: Road profile

        """
        try:
            self.Gdn0 = self.iso_Gdn0[profile_class.upper()]
            return self.generate(L, dx)
        except:
            raise ValueError("Profile name is not predefined.")


if __name__ == '__main__':
    # Create a RoadProfile instance
    testprofile = RoadProfile()
    # Get a road profile
    print testprofile.generate(1, 0.1)
    # Set profile instance to E
    testprofile.set_profile_class("E")
    # Regenerate the road profile with new class
    print testprofile.generate(1, 0.1)
    # Set profile to A and regenerate a road profile
    print testprofile.get_profile_by_class("A", 1, 0.1)
