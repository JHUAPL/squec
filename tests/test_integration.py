import unittest
from squec import squec_solve, Surface, VectorIJ


def _is_symmetric_to_solution(
    solve: list[VectorIJ], dq_list: list[VectorIJ], surface: Surface
):
    return set(solve) == set(dq_list)


class TestSampleProblemsForJordan(unittest.TestCase):

    def test_4_interior_dq_errors_A(self):
        s = Surface((23, 23))
        s.flip_ancilla(VectorIJ(6, 14))
        s.flip_ancilla(VectorIJ(14, 10))
        solve = squec_solve(s)
        self.assertTrue(
            _is_symmetric_to_solution(
                [VectorIJ(7, 13), VectorIJ(9, 11), VectorIJ(11, 11), VectorIJ(13, 11)],
                solve,
                s,
            ),
            solve,
        )

    def test_4_interior_dq_errors_B(self):
        s = Surface((23, 23))
        s.flip_ancilla(VectorIJ(8, 8))
        s.flip_ancilla(VectorIJ(16, 8))
        s.flip_ancilla(VectorIJ(14, 10))
        s.flip_ancilla(VectorIJ(14, 6))
        solve = squec_solve(s)
        self.assertTrue(
            _is_symmetric_to_solution(
                [VectorIJ(15, 9), VectorIJ(9, 7), VectorIJ(11, 7), VectorIJ(13, 7)],
                solve,
                s,
            ),
            solve,
        )

    def test_4_dq_t_pattern_B(self):
        s = Surface((23, 23))
        s.flip_ancilla(VectorIJ(8, 12))
        s.flip_ancilla(VectorIJ(10, 10))
        s.flip_ancilla(VectorIJ(12, 12))
        s.flip_ancilla(VectorIJ(14, 14))
        solve = squec_solve(s)
        self.assertTrue(
            _is_symmetric_to_solution(
                [VectorIJ(9, 11), VectorIJ(13, 13)],
                solve,
                s,
            ),
            solve,
        )

    def test_interior_box(self):
        s = Surface((23, 23))
        s.flip_ancilla(VectorIJ(10, 14))
        s.flip_ancilla(VectorIJ(10, 10))
        s.flip_ancilla(VectorIJ(14, 10))
        s.flip_ancilla(VectorIJ(14, 14))
        solve = squec_solve(s)
        self.assertTrue(
            _is_symmetric_to_solution(
                [
                    VectorIJ(11, 11),
                    VectorIJ(13, 13),
                    VectorIJ(13, 11),
                    VectorIJ(11, 13),
                ],
                solve,
                s,
            ),
            solve,
        )

    def test_hockey_stick_A(self):
        s = Surface((23, 23))
        s.flip_ancilla(VectorIJ(8, 12))
        s.flip_ancilla(VectorIJ(16, 8))

        solve = squec_solve(s)
        self.assertTrue(
            _is_symmetric_to_solution(
                [VectorIJ(15, 9), VectorIJ(13, 9), VectorIJ(11, 9), VectorIJ(9, 11)],
                solve,
                s,
            ),
            solve,
        )

    # def test_hockey_stick_B(self):
    #     s = Surface((23, 23))
    #     s.flip_ancilla(VectorIJ(10, 14))
    #     s.flip_ancilla(VectorIJ(8, 12))
    #     s.flip_ancilla(VectorIJ(12, 12))
    #     s.flip_ancilla(VectorIJ(10, 10))
    #     s.flip_ancilla(VectorIJ(12, 8))
    #     s.flip_ancilla(VectorIJ(16, 8))

    #     solve = squec_solve(s)
    #     self.assertTrue(
    #         _is_symmetric_to_solution(
    #             [VectorIJ(11, 13), VectorIJ(9, 11), VectorIJ(15, 7), VectorIJ(13, 7)],
    #             solve,
    #             s,
    #         ),
    #         solve,
    #     )
