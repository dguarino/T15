import sys
import numpy
from parameters import ParameterSet
from mozaik.models import Model
from mozaik.connectors.meta_connectors import GaborConnector
from mozaik.connectors.modular import ModularSamplingProbabilisticConnector
from mozaik.connectors.fast import OneToOneConnector
from mozaik import load_component
from mozaik.space import VisualRegion


class ThalamoCorticalModel(Model):
    
    required_parameters = ParameterSet({
        'l4_cortex_exc' : ParameterSet, 
        'l4_cortex_inh' : ParameterSet, 
        'pgn' : ParameterSet, 
        'lgn_on' : ParameterSet, 
        'lgn_off' : ParameterSet, 
        'retina' : ParameterSet,
        'visual_field' : ParameterSet 
    })
    
    def __init__(self, sim, num_threads, parameters):
        Model.__init__(self, sim, num_threads, parameters)        
        # Load components
        Retina = load_component(self.parameters.retina.component)
        # Instance
        self.input_layer = Retina(self, self.parameters.retina.params)
      
        # Build and instrument the network
        self.visual_field = VisualRegion(
            location_x=self.parameters.visual_field.centre[0],
            location_y=self.parameters.visual_field.centre[1],
            size_x=self.parameters.visual_field.size[0],
            size_y=self.parameters.visual_field.size[1]
        )


        # PROJECTIONS
        ########################################################

        # LGN
        if True:
            # Load components
            LGN_ON = load_component( self.parameters.lgn_on.component )
            LGN_OFF = load_component( self.parameters.lgn_off.component )

            # Instance
            lgn_on = LGN_ON( self, self.parameters.lgn_on.params )
            lgn_off = LGN_OFF( self, self.parameters.lgn_off.params )

            # Retina-LGN
            OneToOneConnector(
                self,
                'Retina_LGN_ConnectionOn',                  # name
                self.input_layer.sheets['X_ON'],            # source
                lgn_on,                                     # target
                self.parameters.lgn_on.Retina_LGN_ConnectionOn # params
            ).connect()

            OneToOneConnector(
                self,
                'Retina_LGN_ConnectionOff',                 # name
                self.input_layer.sheets['X_OFF'],           # source
                lgn_off,                                    # target
                self.parameters.lgn_off.Retina_LGN_ConnectionOff# params
            ).connect()

        # PGN
        if True:
            # Load components
            PGN = load_component( self.parameters.pgn.component )
            # Instance
            pgn = PGN(self, self.parameters.pgn.params)

            # LGN-PGN
            ModularSamplingProbabilisticConnector(
                self,
                'LGN_PGN_ConnectionOn',                     # name
                lgn_on,            # source
                pgn,                                        # target
                self.parameters.pgn.LGN_PGN_ConnectionOn    # params
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'LGN_PGN_ConnectionOff',                    # name
                lgn_off,           # source
                pgn,                                        # target
                self.parameters.pgn.LGN_PGN_ConnectionOff   # params
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'PGN_PGN_Connection',                       # name
                pgn,                                        # source
                pgn,                                        # target
                self.parameters.pgn.PGN_PGN_Connection      # params
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'PGN_LGN_ConnectionOn',                     # name
                pgn,                                        # source
                lgn_on,            # target
                self.parameters.pgn.PGN_LGN_ConnectionOn    # params
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'PGN_LGN_ConnectionOff',                    # name
                pgn,                                        # source
                lgn_off,           # target
                self.parameters.pgn.PGN_LGN_ConnectionOff   # params
            ).connect()

        if True: # CTC
            # Load components
            CortexExcL4 = load_component(self.parameters.l4_cortex_exc.component)
            CortexInhL4 = load_component(self.parameters.l4_cortex_inh.component)
            # Instance
            cortex_exc_l4 = CortexExcL4(self, self.parameters.l4_cortex_exc.params)
            cortex_inh_l4 = CortexInhL4(self, self.parameters.l4_cortex_inh.params)

            ########################################################
            # THALAMO-CORTICAL
            GaborConnector(
                self,
                lgn_on,
                lgn_off,
                cortex_exc_l4,                                      # target
                self.parameters.l4_cortex_exc.AfferentConnection,   # parameters
                'V1AffConnection'                                   # name
            )

            GaborConnector(
                self,
                lgn_on,
                lgn_off,
                cortex_inh_l4,
                self.parameters.l4_cortex_inh.AfferentConnection,
                'V1AffInhConnection'
            )

            ########################################################
            # CORTICO-CORTICAL
            ModularSamplingProbabilisticConnector(
                self,
                'V1L4ExcL4ExcConnection',
                cortex_exc_l4,
                cortex_exc_l4,
                self.parameters.l4_cortex_exc.L4ExcL4ExcConnection
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'V1L4ExcL4InhConnection',
                cortex_exc_l4,
                cortex_inh_l4,
                self.parameters.l4_cortex_exc.L4ExcL4InhConnection
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'V1L4InhL4ExcConnection',
                cortex_inh_l4,
                cortex_exc_l4,
                self.parameters.l4_cortex_inh.L4InhL4ExcConnection
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'V1L4InhL4InhConnection',
                cortex_inh_l4,
                cortex_inh_l4,
                self.parameters.l4_cortex_inh.L4InhL4InhConnection
            ).connect()

            ########################################################
            # CORTICO-THALAMIC
            ModularSamplingProbabilisticConnector(
                self,
                'V1EffConnectionOn',
                cortex_exc_l4,
                lgn_on,
                self.parameters.l4_cortex_exc.EfferentConnection_LGN
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'V1EffConnectionOff',
                cortex_exc_l4,
                lgn_off,
                self.parameters.l4_cortex_exc.EfferentConnection_LGN
            ).connect()

            ModularSamplingProbabilisticConnector(
                self,
                'V1EffConnectionPGN',
                cortex_exc_l4,
                pgn,
                self.parameters.l4_cortex_exc.EfferentConnection_PGN
            ).connect()
