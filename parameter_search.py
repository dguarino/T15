# Parameter search for Gain control
#
# the function LocalSequentialBackend takes a model with parameters 
# and executes the simulation replacing the parameters listed in the CombinationParameterSearch
#
# usage:
# python parameter_search.py run.py nest param/defaults

from mozaik.meta_workflow.parameter_search import CombinationParameterSearch
from mozaik.meta_workflow.parameter_search import LocalSequentialBackend
import numpy

CombinationParameterSearch(
	LocalSequentialBackend( num_threads=1 ),
	{
    'retina_lgn.params.gain_control.non_linear_gain.contrast_scaler' : [0.05, 0.03, 0.01, 0.009],
    #'retina_lgn.params.gain_control.gain': [3,7,11,15,19,23],
    # 'retina_lgn.LGN_LGN_Connection.weight_functions.f1.params.arborization_constant': [ 100.0, 200.0 ],  # um decay distance from the innervation point
    # 'retina_lgn.LGN_LGN_Connection.base_weight': [ .0001, .005, .001 ], # uS
    # 'retina_lgn.LGN_LGN_Connection.num_samples': [ 10, 30, 50 ],
  }
).run_parameter_search()

