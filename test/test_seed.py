import pickle

from seed.arg import BooleanArg

class TestArg:

    def test_pickle_boolean_arg(self):
        true = BooleanArg(True)
        loaded_true = pickle.loads(pickle.dumps(true))
        assert true.value == loaded_true.value

        false = BooleanArg(True)
        loaded_false = pickle.loads(pickle.dumps(true))
        assert false.value == loaded_false.value