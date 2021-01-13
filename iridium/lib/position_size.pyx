from libc.math cimport pow
from numpy cimport (
uint64_t,
uint32_t,
float64_t
)


cpdef uint64_t calculate_position_size(
        float64_t equity,
        float64_t risk_pct,
        float64_t stop_loss_pips,
        float64_t current_account_vs_quote_rate,
        uint32_t pip_decimal_number):
    """
    Calculate position size using stop loss
    https://www.babypips.com/tools/position-size-calculator
    Balance is the figure of the account which includes all closed trades. Equity is the actual amount of funds in the
    account currently including all open trades.
    :param equity:
    :param risk_pct:
    :param stop_loss_pips:
    :param current_account_vs_quote_rate:
    :param pip_decimal_number:
    :return:
    """
    cdef float64_t loss = equity * risk_pct
    cdef float64_t quote_currency_loss = loss * current_account_vs_quote_rate
    cdef float64_t pip_value = quote_currency_loss / stop_loss_pips
    return pip_value * pow(10, pip_decimal_number)

cdef float64_t calculate_position_value(
        uint64_t position_size,
        float64_t current_pair_rate,
        float64_t current_account_vs_quote_rate):
    """
    Calculate position value
    :param position_size:
    :param current_pair_rate:
    :param current_account_vs_quote_rate:
    :return:
    """
    return position_size * current_pair_rate * (1 / current_account_vs_quote_rate)

