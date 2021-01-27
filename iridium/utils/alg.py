def binary_search(arr, value, low, high, side=None):
    """
    binary search
    :param arr:
    :param value:
    :param low:
    :param high:
    :param side: left, right, None
    :return:
    """
    if high >= low:
        mid = (high + low) // 2
        if arr[mid] == value:
            return mid
        elif arr[mid] > value:
            return binary_search(arr, value, low, mid - 1, side)
        else:
            return binary_search(arr, value, mid + 1, high, side)

    else:
        if arr[low - 1] < value and side == 'left':
            return low - 1
        elif low <= len(arr) - 1 and value < arr[low] and side == 'right':
            return low
        else:
            return -1


def binary_search_left(arr, value):
    return binary_search(arr, value, 0, len(arr) - 1, side='left')


def binary_search_right(arr, value):
    return binary_search(arr, value, 0, len(arr) - 1, side='right')
