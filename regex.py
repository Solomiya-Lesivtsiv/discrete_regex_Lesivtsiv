from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    next_states: list[State] = []

    def __init__(self):
        super().__init__()
    def check_self(self, char):
        return False  # Implement


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return len(char) == 1  # Implement


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.curr_sym = symbol  # Implement

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym  # Implement


class StarState(State):

    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)  # Implement


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        prev_state = self.curr_state
        last_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, last_state)

            if char not in "*+":
                last_state.next_states.append(tmp_next_state)
                prev_state = last_state
                last_state= tmp_next_state
            else:
                prev_state = last_state
                last_state= tmp_next_state

        last_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                if tmp_next_state in prev_state.next_states:
                    prev_state.next_states.remove(tmp_next_state)
                prev_state.next_states.append(new_state)
                new_state.next_states.append(new_state)

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                prev_state.next_states.append(new_state)
                new_state.next_states.append(new_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, text):
        def get_epsilon_closure(states):
            closure = set(states)
            added = True
            while added:
                added = False
                for state in list(closure):
                    for ns in state.next_states:
                        if isinstance(ns, (StarState, PlusState)) and ns not in closure:
                            closure.add(ns)
                            added = True
            return closure

        current = get_epsilon_closure({self.curr_state})

        for char in text:
            next_states = set()
            for state in current:
                for ns in state.next_states:
                    if not isinstance(ns, TerminationState) and ns.check_self(char):
                        next_states.add(ns)

            if not next_states:
                return False

            current = get_epsilon_closure(next_states)
        return any(isinstance(s, TerminationState) or
                any(isinstance(ns, TerminationState) for ns in s.next_states)
                for s in current)

if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
