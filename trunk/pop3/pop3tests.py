import unittest
import pop3
import email


class Pop3Tests(unittest.TestCase):

    with open('test_message.txt', 'rb') as file:
        message = pop3.Mail(file.read())

    def test_is_message(self):
        self.assertIsInstance(self.message.message, email.message.Message)

    def test_get_header(self):
        headers = list(self.message.get_headers('Subject', 'Not Exists',
                                                'To'))
        expected = [('Subject', 'Some Subject'),
                    ('To', 'Слава Вихарев')]
        self.assertSequenceEqual(headers, expected)

    def test_get_message(self):
        message = self.message.get_message()
        expected = '''Hello World\nПривет Мир\nПривет'''
        self.assertEqual(message, expected)

    def test_check_number(self):
        self.assertIsNone(pop3.check_mail_number(-1, 5))
        self.assertIsNone(pop3.check_mail_number(6, 5))
        self.assertIsNone(pop3.check_mail_number(0, 5))
        self.assertIsNone(pop3.check_mail_number('asd', 5))
        self.assertIsNone(pop3.check_mail_number('0', 5))
        self.assertEqual(pop3.check_mail_number('1', 5), 1)
        self.assertEqual(pop3.check_mail_number(5, 5), 5)

    def test_check_address(self):
        good_address_parts = ['address', 'yandex.ru']
        self.assertTrue(pop3.check_address(good_address_parts))
        bad_address_parts = ['address', 'not.exist']
        self.assertFalse(pop3.check_address(bad_address_parts))
        bad_address_parts = ['address', 'not exist']
        self.assertFalse(pop3.check_address(bad_address_parts))


if __name__ == '__main__':
    unittest.main()
