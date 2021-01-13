cdef class Instrument:
    cdef str pair_name

    def __init__(self, pair_name):
        self.pair_name = pair_name

    property base:
        def __get__(self):
            return self.pair_name.split('_')[0]

    property quote:
        def __get__(self):
            return self.pair_name.split('_')[-1]

    property pip_decimal_number:
        def __get__(self):
            if self.quote.upper() == 'JPY':
                return 2
            else:
                return 4

