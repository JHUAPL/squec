from squec.surface import Surface, VectorIJ


def test_can_create_surface_with_tuple():
    surface = Surface((10, 20))
    assert surface.size_ij.i == 10
    assert surface.size_ij.j == 20


def test_can_create_surface_with_tuple_and_origin():
    surface = Surface((10, 20), (20, 20))
    assert surface.size_ij.i == 10
    assert surface.size_ij.j == 20


# def test_create_surface_correct_counts():
#     surface = Surface(VectorIJ(4, 3), (20, 20))
#     assert surface.size_ij.i == 4
#     assert surface.size_ij.j == 3
#     assert len(surface.graph.nodes) == 6
#     assert len(surface.graph.edges) == 7
