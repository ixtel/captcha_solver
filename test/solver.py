from captcha_solver.error import *  # noqa
from captcha_solver import CaptchaSolver
from .base import BaseSolverTestCase, NO_DELAY
from six import string_types


class AntigateUrllibTestCase(BaseSolverTestCase):
    def setup_solver(self):
        self.solver = CaptchaSolver('antigate',
                                    network_backend='urllib',
                                    service_url=self.server.get_url(),
                                    api_key='does not matter')

    def test_post_data(self):
        data = b'foo'
        res = self.solver.captcha_backend.get_submit_captcha_request_data(data)
        body = res['post_data']['body']

        self.assertTrue(isinstance(body, string_types))

    def test_antigate_decoded(self):
        def handler():
            yield b'OK|captcha_id'
            yield b'OK|decoded_captcha'

        self.server.response['data'] = handler()
        self.assertEqual(self.solver.solve_captcha(b'image_data'),
                         'decoded_captcha')

    def test_antigate_no_slot_available(self):
        self.server.response_once['data'] = b'ERROR_NO_SLOT_AVAILABLE'
        self.assertRaises(SolutionTimeoutError, self.solver.solve_captcha,
                          b'image_data', **NO_DELAY)

    def test_antigate_zero_balance(self):
        self.server.response_once['data'] = b'ERROR_ZERO_BALANCE'
        self.assertRaises(BalanceTooLow, self.solver.solve_captcha,
                          b'image_data')

    def test_antigate_unknown_error(self):
        self.server.response_once['data'] = b'UNKNOWN_ERROR'
        self.assertRaises(CaptchaServiceError, self.solver.solve_captcha,
                          b'image_data')

    def test_antigate_unknown_code(self):
        self.server.response_once['code'] = 404
        self.assertRaises(CaptchaServiceError, self.solver.solve_captcha,
                          b'image_data')

    def test_solution_timeout_error(self):
        def handler():
            yield b'OK|captcha_id'
            yield b'CAPCHA_NOT_READY'

        self.server.response['data'] = handler()
        self.assertRaises(SolutionTimeoutError, self.solver.solve_captcha,
                          b'image_data', **NO_DELAY)

    def test_solution_unknown_error(self):
        def handler():
            yield b'OK|captcha_id'
            yield b'UNKNOWN_ERROR'

        self.server.response['data'] = handler()
        self.assertRaises(CaptchaServiceError, self.solver.solve_captcha,
                          b'image_data', **NO_DELAY)

    def test_solution_unknown_code(self):
        def handler():
            yield b'OK|captcha_id'

        self.server.response['data'] = handler()
        self.assertRaises(CaptchaServiceError, self.solver.solve_captcha,
                          b'image_data', **NO_DELAY)


class AntigateGrabTestCase(AntigateUrllibTestCase):
    def setup_solver(self):
        self.solver = CaptchaSolver('antigate',
                                    network_backend='grab',
                                    service_url=self.server.get_url(),
                                    api_key='does not matter')
