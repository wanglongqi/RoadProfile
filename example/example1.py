import pylab as plt
from roadprofile import *
from scipy.signal import periodogram
testprofile = RoadProfile()
profile = testprofile.get_profile_by_class("A",100,0.1)
plt.loglog(*periodogram(profile[1],fs=10))
plt.xlabel("Spatial frequency")
plt.ylabel("PSD")
plt.grid("on")
plt.ylim([1E-8,0.01])
plt.xlim([0.01,5])
plt.show()
