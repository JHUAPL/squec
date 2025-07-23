from squec.surface import VectorIJ


def test_vectorij_equality():
    a = VectorIJ(1, 2)
    b = VectorIJ(1, 2)
    assert a == b


def test_vectorij_clone():
    a = VectorIJ(1, 2)
    b = a.clone()
    assert a == b


def test_vectorij_separation():
    start = VectorIJ(1, 2)
    end = VectorIJ(3, 4)
    assert (start - end) == VectorIJ(-2, -2)
    start = VectorIJ(1, 2)
    end = VectorIJ(3, 4)
    assert (start.separation_from(end)) == VectorIJ(-2, -2)
    start = VectorIJ(1, 2)
    end = VectorIJ(10000, 4)
    assert (VectorIJ.separation(start, end)) == VectorIJ(-9999, -2)


def test_add_with_vectorij():
    start = VectorIJ(1, 2)
    end = VectorIJ(3, 4)
    assert (start + end) == VectorIJ(4, 6)


def test_add_with_tuple():
    start = VectorIJ(1, 2)
    end = (3, 4)
    assert (start + end) == VectorIJ(4, 6)


def test_add_with_list():
    start = VectorIJ(1, 2)
    end = [3, 4]
    assert (start + end) == VectorIJ(4, 6)
