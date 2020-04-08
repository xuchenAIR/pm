import heuristic.net as net

DEPENDENCY_THRESH = 'dependency_tresh'
AND_MEASURE_THRESH = 'and_measure_tresh'
MIN_DFG_OCCUR = 'min_dfg_occur'
MIN_ACT_COUNT = 'min_act_count'
DFG_PRE_CLEAN_NOISE_THRESH = 'dfg_pre_clean_noise_tresh'
LOOP_LENGTH_TWO_THRESH = 'loop_length_two_tresh'
default_parameters = {DEPENDENCY_THRESH:0.5,AND_MEASURE_THRESH:0.65,MIN_ACT_COUNT:1,MIN_DFG_OCCUR:1,DFG_PRE_CLEAN_NOISE_THRESH:0.05,LOOP_LENGTH_TWO_THRESH:0.5}

PARAM_MOST_COMMON_PATHS = 'most_common_paths'

class hueristic_obj(object):
    activity_key = None
    start_activities = None
    end_activities = None
    activity_occs = None
    activities = None
    dfg = None
    dfg_step_two = None
    triples = None
    parameters = {}



    def __init__(self,start_activities,end_activities,activity_occs,activities,dfg,dfg_step_two,triples,activity_key='concept:name',parameters=None):
        self.activity_key = activity_key
        self.start_activities = start_activities
        self.end_activities = end_activities
        self.activities = activities
        self.activity_occs = activity_occs
        self.dfg = dfg
        self.dfg_step_two = dfg_step_two
        self.triples = triples
        self.parameters = parameters
        self.get_hueristic_result()

    def get_hueristic_result(self):
        parameters = self.parameters
        if parameters is None:
            parameters = {}
        dependency_tresh = parameters[
            DEPENDENCY_THRESH] if DEPENDENCY_THRESH in parameters else default_parameters[DEPENDENCY_THRESH]
        and_measure_tresh = parameters[
            AND_MEASURE_THRESH] if AND_MEASURE_THRESH in parameters else default_parameters[AND_MEASURE_THRESH]
        min_act_count = parameters[
            MIN_ACT_COUNT] if MIN_ACT_COUNT in parameters else default_parameters[MIN_ACT_COUNT]
        min_dfg_occur = parameters[
            MIN_DFG_OCCUR] if MIN_DFG_OCCUR in parameters else default_parameters[MIN_DFG_OCCUR]
        dfg_pre_clean_noise_tresh = parameters[
            DFG_PRE_CLEAN_NOISE_THRESH] if DFG_PRE_CLEAN_NOISE_THRESH in parameters else default_parameters[DFG_PRE_CLEAN_NOISE_THRESH]
        loop_length_two_tresh = parameters[
            LOOP_LENGTH_TWO_THRESH] if LOOP_LENGTH_TWO_THRESH in parameters else default_parameters[LOOP_LENGTH_TWO_THRESH]
        heu_net = net.HeuristicsNet(self.dfg, activities=self.activities, activities_occurrences=self.activity_occs,
                                start_activities=self.start_activities, end_activities=self.end_activities,
                                dfg_step_two=self.dfg_step_two,
                                triples=self.triples)
        heu_net.hueristic_calculate(dependency_tresh,and_measure_tresh,min_act_count,min_dfg_occur,dfg_pre_clean_noise_tresh,loop_length_two_tresh)
        return heu_net


