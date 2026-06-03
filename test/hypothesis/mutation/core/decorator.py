from core.mutation import Mutation


def mutation(name: str):
    """
    Minimal decorator :
    trandform function to mutation
    """

    def wrapper(fn):

        return Mutation(
            name=name,
            fn=fn,
        )

    return wrapper