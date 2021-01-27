from iridium.utils.alg import binary_search_left, binary_search_right


def test_binary_search():
    arr = [1, 3, 5, 7, 9]
    assert binary_search_left(arr, -1) == -1
    assert binary_search_left(arr, 1) == 0
    assert binary_search_left(arr, 2) == 0
    assert binary_search_left(arr, 4) == 1
    assert binary_search_left(arr, 6) == 2
    assert binary_search_left(arr, 8) == 3
    assert binary_search_left(arr, 9) == 4
    assert binary_search_left(arr, 10) == 4

    assert binary_search_right(arr, -1) == 0
    assert binary_search_right(arr, 1) == 0
    assert binary_search_right(arr, 2) == 1
    assert binary_search_right(arr, 4) == 2
    assert binary_search_right(arr, 6) == 3
    assert binary_search_right(arr, 8) == 4
    assert binary_search_right(arr, 9) == 4
    assert binary_search_right(arr, 10) == -1
