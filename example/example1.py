import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pylab as plt
from scipy.signal import periodogram
from roadprofile import RoadProfile

testprofile = RoadProfile()
profile = testprofile.get_profile_by_class("A", 100, 0.1)
plt.loglog(*periodogram(profile.profile, fs=10))
plt.xlabel("Spatial frequency")
plt.ylabel("PSD")
plt.grid(True)
plt.ylim([1E-8, 0.01])
plt.xlim([0.01, 5])
plt.show()
