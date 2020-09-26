"""
This file contains the default parameter values for various system configuration settings.
Each of the values below can be overridden by providing a different value in CEP.__init__ or CEP.run.
"""
from evaluation.EvaluationMechanismTypes import EvaluationMechanismTypes
from misc.SelectionStrategies import SelectionStrategies
from plan.IterativeImprovement import IterativeImprovementType, IterativeImprovementInitType
from plan.TreeCostModels import TreeCostModels
from plan.TreePlanBuilderTypes import TreePlanBuilderTypes
from plan.MultiPatternEvaluationApproach import MultiPatternEvaluationApproach


# general settings
DEFAULT_EVALUATION_MECHANISM_TYPE = EvaluationMechanismTypes.TREE_BASED

# plan generation-related defaults
DEFAULT_TREE_PLAN_BUILDER = TreePlanBuilderTypes.TRIVIAL_LEFT_DEEP_TREE
DEFAULT_TREE_COST_MODEL = TreeCostModels.INTERMEDIATE_RESULTS_TREE_COST_MODEL

# default selection strategies
PRIMARY_SELECTION_STRATEGY = SelectionStrategies.MATCH_ANY
SECONDARY_SELECTION_STRATEGY = SelectionStrategies.MATCH_SINGLE

# tree storage settings
SHOULD_SORT_STORAGE = False
CLEANUP_INTERVAL = 10  # the default number of pattern match additions between subsequent storage cleanups
PRIORITIZE_SORTING_BY_TIMESTAMP = True

# iterative improvement defaults
ITERATIVE_IMPROVEMENT_TYPE = IterativeImprovementType.SWAP_BASED
ITERATIVE_IMPROVEMENT_INIT_TYPE = IterativeImprovementInitType.RANDOM

# multi pattern approach
DEFAULT_MULTI_PATTERN_APPROACH = MultiPatternEvaluationApproach.TRIVIAL_SHARING_LEAVES