from typing import List, Any


class Fn:
    """
    The component of a `Seed`
    """
    def __init__(self, fn_name: str, *args) -> None:
        self.fn_name: str = fn_name
        self.args: List[Any] = list(args)

    def execute(self, obj: object):
        real_fn = getattr(obj, self.fn_name)
        real_fn(*tuple(self.args))


class Seed:
    """
    The fuzzing seed
    """
    def __init__(self) -> None:
        self.fns: List[Fn] = []
        self.mutations: List[str] = []

    def execute(self, obj: object):
        for fn in self.fns:
            fn.execute(obj)

    def __getitem__(self, index) -> Fn:
        return self.fns[index]
