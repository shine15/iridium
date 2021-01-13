from numpy cimport (
uint32_t,
float64_t,
uint64_t
)

cdef float64_t calculate_gains_losses(
        float64_t pip_change,
        uint64_t units,
        float64_t current_account_vs_quote_rate,
        uint32_t pip_decimal_number)

cpdef float64_t calculate_margin_used(uint64_t units,
                                     float64_t current_account_vs_base_rate,
                                     uint32_t leverage)

cpdef float64_t calculate_margin_available(float64_t nav,
                                           float64_t margin_used)