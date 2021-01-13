from functools import wraps
from inspect import getfullargspec


def expect_types(**named):
    for name, type_ in named.items():
        if not isinstance(type_, (type, tuple)):
            raise TypeError(
                "expect_types() expected a type or tuple of types for "
                "argument '{name}', but got {type_} instead.".format(
                    name=name, type_=type_,
                )
            )

    def wrapped_func(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            func_args = getfullargspec(func).args
            kwargs.update(dict(zip(func_args, args)))
            for attr_name, attr_type in named.items():
                if not isinstance(kwargs[attr_name], attr_type):
                    raise TypeError(
                        'Argument %r is not of type %s' % (attr_name, attr_type)
                    )
            return func(**kwargs)
        return decorator
    return wrapped_func

