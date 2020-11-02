from datetime import timedelta
from typing import List

from base.Event import Event
from base.Formula import CompositeFormula
from base.PatternMatch import PatternMatch
from misc.Utils import recursive_powerset_generator
from tree.Node import Node
from tree.UnaryNode import UnaryNode


class KleeneClosureNode(UnaryNode):
    """
    An internal node representing a Kleene closure operator.
    It generates and propagates sets of partial matches provided by its sole child.
    """
    def __init__(self, sliding_window: timedelta, min_size, max_size, parent: Node = None):
        super().__init__(sliding_window, parent)
        self.__min_size = min_size
        self.__max_size = max_size

    def handle_new_partial_match(self, partial_match_source: Node):
        """
        Reacts upon a notification of a new partial match available at the child by generating, validating, and
        propagating all sets of partial matches containing this new partial match.
        Note: this method strictly assumes that the last partial match in the child storage is the one to cause the
        method call (could not function properly in a parallelized implementation of the evaluation tree).
        """
        if self._child is None:
            raise Exception()  # should never happen

        new_partial_match = self._child.get_last_unhandled_partial_match()
        self._child.clean_expired_partial_matches(new_partial_match.last_timestamp)

        # create partial match sets containing the new partial match that triggered this method
        child_matches_powerset = self.__create_child_matches_powerset()

        for partial_match_set in child_matches_powerset:
            # create and propagate the new match
            events_for_partial_match = KleeneClosureNode.__partial_match_set_to_event_list(partial_match_set)
            self._validate_and_propagate_partial_match(events_for_partial_match)

    def _validate_new_match(self, events_for_new_match: List[Event]):
        """
        Validates the condition stored in this node on the given set of events.
        """
        return self._condition.eval([e.payload for e in events_for_new_match])

    def __create_child_matches_powerset(self):
        """
        This method is a generator returning all subsets of currently available partial matches of this node child.
        As this method is always invoked following a notification regarding a new partial match received from the child,
        only the subsets containing this new partial match (which is assumed to be the last partial match in the child
        list) are generated.
        The subsets are enforced to satisfy the minimal and maximal size constraints.
        The maximal size constraint is enforced recursively to save as many computations as possible.
        The minimal size constraint on the other hand is enforced via post-processing filtering due to negligible
        overhead.
        """
        child_partial_matches = self._child.get_partial_matches()
        if len(child_partial_matches) == 0:
            return []
        last_partial_match = child_partial_matches[-1]
        # create subsets for all but the last element
        actual_max_size = self.__max_size if self.__max_size is not None else len(child_partial_matches)
        generated_powerset = recursive_powerset_generator(child_partial_matches[:-1], actual_max_size - 1)
        # add the last item to all previously created subsets
        result_powerset = [item + [last_partial_match] for item in generated_powerset]
        # enforce minimal size limit
        result_powerset = [item for item in result_powerset if self.__min_size <= len(item)]
        return result_powerset

    def apply_formula(self, formula: CompositeFormula):
        """
        The default implementation is overridden to extract KC conditions from the given composite condition.
        """
        self._propagate_condition(formula)
        names = {event_def.name for event_def in self.get_event_definitions()}
        self._condition = formula.get_formula_of(names, True)
        formula.consume_formula_of(names, True)

    def get_structure_summary(self):
        return "KC", self._child.get_structure_summary()

    @staticmethod
    def __partial_match_set_to_event_list(partial_match_set: List[PatternMatch]):
        """
        Converts a set of partial matches into a single list containing all primitive events of the partial
        matches in the set.
        TODO: this is not the way this operator should work!
        """
        min_timestamp = None
        max_timestamp = None
        events = []
        for match in partial_match_set:
            min_timestamp = match.first_timestamp if min_timestamp is None else min(min_timestamp, match.first_timestamp)
            max_timestamp = match.last_timestamp if max_timestamp is None else max(max_timestamp, match.last_timestamp)
            events.extend(match.events)

        return events
