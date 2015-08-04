# -*- coding: utf-8 -*-
"""
This is implementation of a full recursive model of thalamo-cortical connectvity
"""
import sys
from pyNN import nest
import mozaik
from mozaik.controller import run_workflow, setup_logging
from model import ThalamoCorticalModel
from experiments import create_experiments
from mozaik.storage.datastore import Hdf5DataStore,PickledDataStore
from analysis_and_visualization import perform_analysis_and_visualization
from parameters import ParameterSet


try:
    from mpi4py import MPI
except ImportError:
    MPI = None
if MPI:
    mpi_comm = MPI.COMM_WORLD
MPI_ROOT = 0

logger = mozaik.getMozaikLogger()


# Manage what is executed
# a set of variable here to manage the type of experiment and whether the pgn, cortex are there or not.
withPGN = True
withV1 = True


if True:
    data_store,model = run_workflow('T15', ThalamoCorticalModel, create_experiments)

    if withPGN: # PGN
        model.connectors['LGN_PGN_ConnectionOn'].store_connections(data_store)    
        model.connectors['LGN_PGN_ConnectionOff'].store_connections(data_store)    
        model.connectors['PGN_PGN_Connection'].store_connections(data_store)    
        model.connectors['PGN_LGN_ConnectionOn'].store_connections(data_store)    
        model.connectors['PGN_LGN_ConnectionOff'].store_connections(data_store)    
    if withV1: # CORTEX
        model.connectors['V1L4ExcL4ExcConnection'].store_connections(data_store)    
        model.connectors['V1L4ExcL4InhConnection'].store_connections(data_store)    
        model.connectors['V1L4InhL4ExcConnection'].store_connections(data_store)    
        model.connectors['V1L4InhL4InhConnection'].store_connections(data_store)    
        model.connectors['V1AffConnectionOn'].store_connections(data_store)    
        model.connectors['V1AffConnectionOff'].store_connections(data_store)    
        model.connectors['V1AffInhConnectionOn'].store_connections(data_store)    
        model.connectors['V1AffInhConnectionOff'].store_connections(data_store)    
        model.connectors['V1EffConnectionOn'].store_connections(data_store)    
        model.connectors['V1EffConnectionOff'].store_connections(data_store)    
        model.connectors['V1EffConnectionPGN'].store_connections(data_store)    
    data_store.save()
    
else: 
    setup_logging()
    data_store = PickledDataStore(load=True,parameters=ParameterSet({'root_directory':'T15_data_____', 'store_stimuli' : False}),replace=True)
    logger.info('Loaded data store')
    data_store.save()

if mpi_comm.rank == MPI_ROOT:
    perform_analysis_and_visualization(data_store)
