from server.services.sum import SumService


def test_add_positive_numbers():
    assert SumService.add(2, 3) == 5


def test_add_negative_numbers():
    assert SumService.add(-1, -2) == -3


def test_add_floats():
    assert SumService.add(1.5, 2.5) == 4.0


def test_add_zero():
    assert SumService.add(0, 5) == 5
