###########################
# Receptive field plot
# Domenico Guarino

import numpy as np
from scipy import ndimage

# import matplotlib.pyplot as plt
import pylab as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.mlab import griddata


def F_1d(x, A, sigma):
    return A * np.exp(-(x**2) / (2*sigma**2))

def F_2d(x, y, A, sigma):
    return A * np.exp(-(x**2 + y**2) / (2*sigma**2))


def meshgrid3D(x, y, z):
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    mult_fact = np.ones((len(x), len(y), len(z)))
    nax = np.newaxis
    return x[:, nax, nax] * mult_fact, \
           y[nax, :, nax] * mult_fact, \
           z[nax, nax, :] * mult_fact


def meshgrid2D(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    mult_fact = np.ones((len(x), len(y)))
    nax = np.newaxis
    return x[:, nax] * mult_fact, \
           y[nax, :] * mult_fact



###########
# Visual Space
# x = np.arange(-10, 10, 0.2)
# y = np.arange(-10, 10, 0.2)


###########
# spatiotemporalfilter.py > SpatioTemporalReceptiveField

# Current actual values
# self.width 12.0
# self.height 12.0
# self.duration 100.0
# quantize:  0.2 0.2 7.0
width = 12.      # (degrees) x-dimension size
height = 12.     # (degrees) y-dimension size
duration = 100. # (ms) length of the temporal axis of the RF
dx = 0.2 		# The number of pixels along x axis.
dy = 0.2 		# The number of pixels along y axis.
dt = 7.0 		# The number of time bins along the t axis.
########
# DoG RF
Ac = 1.0 # CaiDeAngelisFreeman1997
As = 0.11 # CaiDeAngelisFreeman1997 (proportional)
sigma_c = 0.5 # deg Hammond1974, BoninManteCarandini2005, SceniakChatterjeeCallaway2006 (0.5)
sigma_s = 1.5 # deg BoninManteCarandini2005, SceniakChatterjeeCallaway2006 (1.4)
# sigma_c = 0.528030 # mozaik generated (rounding?)
# sigma_s = 1.570796 # 

nx = np.ceil(width/dx)
ny = np.ceil(height/dy)
nt = np.ceil(duration/dt)
w = nx * dx
h = ny * dy
d = nt * dt

# vector of positions along the x and y dims
# each goes from 0 to width-dx, with w/dx step
# (+ dx/2.0 - w/2.0) x and y are the coordinates of the centre of each pixel
x = np.linspace( 0.0, w - dx, w/dx ) + dx/2.0 - w/2.0
y = np.linspace( 0.0, h - dy, h/dy ) + dx/2.0 - h/2.0
# t is the time at the beginning of each timestep
t = np.arange( 0.0, d, dt )

# X, Y = np.meshgrid(x, y)
X, Y = meshgrid2D(y, x)  # x,y are reversed because (x,y) <--> (j,i)
# X, Y, T = meshgrid3D(y, x, t)  # x,y are reversed because (x,y) <--> (j,i)

#def stRF_2d(x, y, t, p):
# kernel = func( X, Y, T, self.func_params )

# fcm = F_1d(x, Ac, sigma_c)
# fsm = F_1d(x, As, sigma_s)
fcm = F_2d(X, Y, Ac, sigma_c)
fsm = F_2d(X, Y, As, sigma_s)
# Linear Receptive Field
kernel = (fcm - fsm)
print "kernel.shape:",kernel.shape

# normalize to make the kernel sum quasi-independent of the quantization
kernel = kernel/(nx * ny)  

##########
# Feature tuning

# cycle over frequencies
label = 'frequency'
# feature = [0.1, 0.19, 0.27, 0.31, 0.35, 0.37, 0.39, 0.41, 0.43, 0.45, 0.49, 0.51, 0.55, 0.59, 0.65, 0.75, 0.85, 0.95, 1.0]
feature = [0.5]
# #single best frequency
# best_freq = 0.45

# cycle over sizes
# label = 'size'
# feature = np.arange(1,50) # radiuses from 1 to 50
# center_x = kernel.shape[0] / 2
# center_y = kernel.shape[1] / 2
# oy,ox = np.ogrid[ -center_x : kernel.shape[0]-center_x, -center_y : kernel.shape[1]-center_y ]

tuning = []
for f in feature:
	# print "feat: ", f

	##########
	# sinusoidal drifting grating
	freq = f * 2*np.pi
	# freq = best_freq * np.pi
	phase = np.pi/2
	dg = np.sin( freq * X + phase )
	# square gratings
	# dg[dg>0]=1 
	# dg[dg<0]=-1
	# only drifting gratings positive (background = 0, see later)
	# dg = (dg+1)/2 # positive between 0 and 1

	##########
	# disk
	if label=='size':
		mask = ox*ox + oy*oy <= f*f # feature f is now radius
		dg[~mask] = 0 # ~mask logical not to mask outside the disk
		# print dg[45][45] # test one position

	##########
	# convolution
	dg = (dg+1)/2 # positive between 0 and 1
	view = dg * kernel

	##########
	# sum view
	tot = np.sum( view ) # all axes (no time kernel)
	# print tot

	tuning.append(tot)


##########
# plot the points
print tuning


##############################
kern = file("/home/do/mozaik/mozaik/mozaik-contrib/T15/param/kernel.npy", 'r')
mozaik_kernel = np.load(kern)
kern.close()

grat = file("/home/do/mozaik/mozaik/mozaik-contrib/T15/param/view.npy", 'r')
mozaik_dg = np.load(grat)
grat.close()
##############################
print 
mk = mozaik_kernel[:,:,0] # discard second time point
print "mozaik_kernel",mk.shape
print "kernel",kernel.shape
print
print "mozaik_dg",mozaik_dg.shape
print "dg",dg.shape


def normalized( a ):
	row_sums = a.sum(axis=1)
	return a / row_sums[:, np.newaxis] # broadcast


# print "original",mk
print " -------------- KERNELS ------------- "
mk = normalized( mk )
print "mozaik",mk
kernel = normalized( kernel )
print "analyt",kernel
print
print mk-kernel


print " -------------- GRATINGS ------------- "
# mozaik_dg = normalized( mozaik_dg )
# print "mozaik",mozaik_dg
# dg = normalized( dg )
# print "analyt",dg
# print 
# print mozaik_dg-dg


#######
# Plotting

# # tuning curve
# plt.figure()
# plt.xlabel( label )
# plt.ylabel( 'convolution' )
# plt.plot( feature, tuning, 'o-' )

# RF (last one)
# figa = plt.figure()
# ax = figa.gca(projection='3d')
# surf = ax.plot_surface( X, Y, kernel, rstride=1, cstride=1, cmap=cm.jet, linewidth=0.1, antialiased=True )
# figa.colorbar(surf)

# plt.figure()
# plt.imshow(kernel,vmin=-10e-5,vmax=10e-5,cmap=cm.seismic)
plt.figure()
plt.imshow(dg,cmap=cm.gray)
plt.figure()
plt.imshow(mozaik_dg,cmap=cm.gray)

# # Input (drifting grating)
# figb = plt.figure()
# ax = figb.gca(projection='3d')
# surf = ax.plot_surface( X, Y, dg, rstride=1, cstride=1, cmap=cm.jet, linewidth=0.1, antialiased=True )
# figb.colorbar(surf)

# # view
# figc = plt.figure()
# ax = figc.gca(projection='3d')
# surf = ax.plot_surface( X, Y, view, rstride=1, cstride=1, cmap=cm.jet, linewidth=0.1, antialiased=True )
# figc.colorbar(surf)

plt.show()
