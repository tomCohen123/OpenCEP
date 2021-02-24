from abc import ABC, abstractmethod
from base import Pattern
from misc import DefaultConfig
from plan import TreePlanBuilder
from plan.LeftDeepTreeBuilders import TrivialLeftDeepTreeBuilder
from plan.TreeCostModels import TreeCostModels
from plan.TreePlanBuilderTypes import TreePlanBuilderTypes
from statistics_collector.StatisticsWrapper import StatisticsWrapper


class Optimizer(ABC):
    """
    An abstract class for optimizer.
    """

    def __init__(self, tree_plan_builder: TreePlanBuilder):
        self._tree_plan_builder = tree_plan_builder

    @abstractmethod
    def is_need_optimize(self, new_statistics: dict, pattern: Pattern):
        """
        Asks if it's necessary to optimize the tree based on the new statistics.
        """
        raise NotImplementedError()

    @abstractmethod
    def build_new_tree_plan(self, new_statistics: dict, pattern: Pattern):
        raise NotImplementedError()

    def build_initial_tree_plan(self, new_statistics: dict, cost_model_type: TreeCostModels,
                                pattern: Pattern):

        non_prior_tree_plan_builder = self.build_non_prior_tree_plan_builder(cost_model_type, pattern)
        if non_prior_tree_plan_builder is not None:
            self._tree_plan_builder, temp_tree_plan_builder = non_prior_tree_plan_builder, self._tree_plan_builder
            initial_tree_plan = self.build_new_tree_plan(new_statistics, pattern)
            self._tree_plan_builder = temp_tree_plan_builder
        else:
            initial_tree_plan = self.build_new_tree_plan(new_statistics, pattern)
        return initial_tree_plan

    @staticmethod
    def build_non_prior_tree_plan_builder(cost_model_type: TreeCostModels, pattern: Pattern):
        non_prior_tree_plan_builder = None
        if pattern.statistics is None:
            if DefaultConfig.DEFAULT_TREE_PLAN_BUILDER == TreePlanBuilderTypes.TRIVIAL_LEFT_DEEP_TREE:
                non_prior_tree_plan_builder = TrivialLeftDeepTreeBuilder(cost_model_type)
            else:
                raise Exception("Unknown tree plan builder type: %s" % (DefaultConfig.DEFAULT_TREE_PLAN_BUILDER,))
        return non_prior_tree_plan_builder


class TrivialOptimizer(Optimizer):
    """
    Represents the trivial optimizer that always says to re-optimize the tree, ignoring the statistics.
    """

    def is_need_optimize(self, new_statistics: dict, pattern: Pattern):
        return True

    def build_new_tree_plan(self, new_statistics: dict, pattern: Pattern):
        tree_plan = self._tree_plan_builder.build_tree_plan(new_statistics, pattern)
        return tree_plan


class StatisticsChangesAwareOptimizer(Optimizer):
    """
    Represents the optimizer that is aware of the changes in the statistics,
    i.e if one of the statistics is changed by constant t then the optimizer will say that tree optimization is needed.
    """

    def __init__(self, tree_plan_builder: TreePlanBuilder, type_to_changes_aware_functions_map: dict):
        super().__init__(tree_plan_builder)
        self.__prev_statistics = None
        self.__type_to_changes_aware_tester_map = type_to_changes_aware_functions_map

    def is_need_optimize(self, new_statistics: dict, pattern: Pattern):
        for new_statistics_type, new_statistics in new_statistics.items():
            prev_statistics = self.__prev_statistics[new_statistics_type]
            if self.__type_to_changes_aware_tester_map[new_statistics_type].is_changed_by_t(new_statistics,
                                                                                            prev_statistics):
                return True
        return False
        # return self._prev_statistics is None or self.is_changed_by_t(new_statistics.statistics, self._prev_statistics)

    def build_new_tree_plan(self, new_statistics: dict, pattern: Pattern):
        self.__prev_statistics = new_statistics
        tree_plan = self._tree_plan_builder.build_tree_plan(new_statistics, pattern)
        return tree_plan

    def is_changed_by_t(self, new_statistics, old_statistics):
        """
        Checks if there was a changes in one of the statistics by a factor of t.
        """
        raise NotImplementedError()


class InvariantsAwareOptimizer(Optimizer):
    """
    Represents the invariants aware optimizer that checks if at least one invariant was violated.
    """

    def __init__(self, tree_plan_builder: TreePlanBuilder):
        super().__init__(tree_plan_builder)
        self._invariants = None

    def is_need_optimize(self, new_statistics: dict, pattern: Pattern):
        return self._invariants is None or self._invariants.is_invariants_violated(new_statistics, pattern)

    def build_new_tree_plan(self, new_statistics: dict, pattern: Pattern):
        tree_plan, self._invariants = self._tree_plan_builder.build_tree_plan(new_statistics, pattern)
        return tree_plan

    def build_initial_tree_plan(self, new_statistics: dict, cost_model_type: TreeCostModels,
                                pattern: Pattern):
        non_prior_tree_plan_builder = self.build_non_prior_tree_plan_builder(cost_model_type, pattern)
        if non_prior_tree_plan_builder is not None:
            return non_prior_tree_plan_builder.build_tree_plan(new_statistics, pattern)
        return self.build_new_tree_plan(new_statistics, pattern)
