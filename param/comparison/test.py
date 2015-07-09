import numpy
from pyNN.nest import *
from pyNN.space import Line

import matplotlib.pyplot as plt


def test_sim(on_or_off_grid, sim_time):
    setup(timestep=1.0, min_delay=1.0, max_delay=1.0, spike_precision=on_or_off_grid)
    # struct = Line(y=0.0, x0=0.0, z=0.0, dx=1.0)
    src = Population(10, SpikeSourceArray(spike_times=[0.5]))
    print "src:", len(src)
    print src.positions
    print src.structure
    cm        = 250.0
    tau_m     =  10.0
    tau_syn_E =   1.0
    weight    = cm/tau_m * numpy.power(tau_syn_E/tau_m, -tau_m/(tau_m-tau_syn_E)) * 20.5

    nrn = Population(
        src.size, 
        IF_curr_exp(cm=cm, tau_m=tau_m, tau_syn_E=tau_syn_E, tau_refrac=2.0, v_thresh=20.0, v_rest=0.0, v_reset=0.0, i_offset=0.0),
        structure = src.structure
    )
    nrn.initialize(v=0.0)
    for i in range(nrn.size):
        nrn[i].position = src[i].position
    # print "nrn before:", nrn.positions
    # nrn.positions = src.positions.copy()
    # print "nrn after:", nrn.positions

    prj = Projection(src, nrn, OneToOneConnector(), StaticSynapse(weight=weight))
    nrn.record('v')
    run(sim_time)
    return nrn.get_data().segments[0].analogsignalarrays[0]


sim_time = 10.0
off = test_sim('off_grid', sim_time)
on  = test_sim('on_grid', sim_time)



def plot_data(pos, on, off, ylim, with_legend=False):
    ax = plt.subplot(1, 2, pos)
    ax.plot(off.times, off, color='0.7', linewidth=7, label='off-grid')
    ax.plot(on.times, on, 'k', label='on-grid')
    ax.set_ylim(*ylim)
    ax.set_xlim(0, 9)
    ax.set_xlabel('time [ms]')
    ax.set_ylabel('V [mV]')
    if with_legend:
        plt.legend()

plot_data(1, on, off, (-0.5, 21), with_legend=True)
plot_data(2, on, off, (-0.05, 2.1))
plt.show()