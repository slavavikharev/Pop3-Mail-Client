import unittest
import mail
import mailclient
import email


class Pop3Tests(unittest.TestCase):

    with open('test_message.txt', 'rb') as file:
        message = mail.Mail(file.read())

    client = mailclient.MailClient('a@a.com', 'pass')

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
        self.assertFalse(self.client.check_mail_number('-1', 5))
        self.assertFalse(self.client.check_mail_number('0', 5))
        self.assertTrue(self.client.check_mail_number('1', 5), 1)
        self.assertTrue(self.client.check_mail_number('5', 5))
        self.assertFalse(self.client.check_mail_number('6', 5))
        self.assertFalse(self.client.check_mail_number('asd', 5))

    def test_check_address(self):
        address = 'address@yandex.ru'
        self.assertTrue(mailclient.check_address(address))
        address = 'domain.ru'
        self.assertFalse(mailclient.check_address(address))
        address = '@s.com'
        self.assertFalse(mailclient.check_address(address))
        address = 'a@.com'
        self.assertFalse(mailclient.check_address(address))
        address = 'a@com'
        self.assertFalse(mailclient.check_address(address))


if __name__ == '__main__':
    unittest.main()
