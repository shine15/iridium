from numpy cimport (
uint64_t,
uint32_t,
float64_t
)
from libc.math cimport pow

cdef float64_t calculate_pip_value(
        uint64_t units,
        float64_t current_account_vs_quote_rate,
        uint32_t pip_decimal_number):
    """
    Calculate Pip value
    https://www.fxpro.com/trading-tools/calculators/pip
    :param units:
    :param current_account_vs_quote_rate: Account currency vs quote currency rate
    :param pip_decimal_number:
    :return: pip value
    """
    cdef float64_t pip = 1 / pow(10, pip_decimal_number)
    return units * pip / current_account_vs_quote_rate

cdef float64_t calculate_gains_losses(
        float64_t pip_change,
        uint64_t units,
        float64_t current_account_vs_quote_rate,
        uint32_t pip_decimal_number):
    """
    Calculate gain loss
    https://www.oanda.com/forex-trading/analysis/profit-calculator/
    :param pip_change:
    :param units:
    :param current_account_vs_quote_rate:
    :param pip_decimal_number:
    :return:
    """
    return pip_change * \
           calculate_pip_value(
               units,
               current_account_vs_quote_rate,
               pip_decimal_number)

cpdef float64_t calculate_margin_used(uint64_t units,
                                     float64_t current_account_vs_base_rate,
                                     uint32_t leverage):
    """
    Calculate margin used for currency pair
    https://www.oanda.com/resources/legal/united-states/legal/margin-rules
    :param units:
    :param current_account_vs_base_rate:
    :param leverage:
    :return:
    """
    return units * (1 / current_account_vs_base_rate) * (1.0 / leverage)

def check_margin_call(float64_t nav,
                      float64_t margin_used):
    """
    https://www.oanda.com/resources/legal/australia/legal/margin-rules
    A margin closeout will be triggered when the Margin Closeout Value declines to half, or less than half, of the Margin Used.
    :param nav: net assets value
    :param margin_used:
    :return: True or False
    """
    return nav <= margin_used / 2

cpdef float64_t calculate_margin_available(float64_t nav,
                                           float64_t margin_used):
    """
    Calculate margin available
    :param nav: net asset value
    :param margin_used:
    :return: margin available
    """
    cdef float64_t margin_available = nav - margin_used
    return margin_available if margin_available > 0 else 0.0
