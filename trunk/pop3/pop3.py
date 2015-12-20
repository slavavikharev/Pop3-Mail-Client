import socket
import ssl
import getpass
import email
import base64
import quopri

CR = b'\r'
LF = b'\n'
CRLF = CR + LF

MAIL_LIST = {
    'mail.ru': ('pop.mail.ru', 995),
    'bk.ru': ('pop.mail.ru', 995),
    'inbox.ru': ('pop.mail.ru', 995),
    'list.ru': ('pop.mail.ru', 995),
    'yandex.ru': ('pop.yandex.ru', 995),
    'gmail.com': ('pop.gmail.com', 995),
    'yahoo.com': ('pop.mail.yahoo.com', 995)
}


class Pop3:
    def __init__(self, host, port):
        """
        :type host: str
        :type port: int
        """
        self.host = host
        self.port = port
        self.sock = self.create_socket()
        self.file = self.sock.makefile('rb')
        self.welcome = self.get_resp()

    def create_socket(self):
        """Returns ssl-wrapped socket"""
        sock = socket.create_connection((self.host, self.port))
        sock = ssl.wrap_socket(sock)
        return sock

    def get_line(self):
        """Returns line from server"""
        line = self.file.readline()
        if not line:
            raise EOFError('-ERR EOF')
        if line[-2:] == CRLF:
            return line[:-2]
        if line[:1] == CR:
            return line[1:-1]
        return line[:-1]

    def get_resp(self):
        """
        Returns singleline response
        or raises come error
        """
        resp = self.get_line()
        if not resp.startswith(b'+'):
            raise ConnectionError(resp)
        return resp

    def get_long_resp(self):
        """Returns multiline response"""
        resp = self.get_resp()
        lines = []
        line = self.get_line()
        while line != b'.':
            if line.startswith(b'..'):
                line = line[1:]
            lines.append(line)
            line = self.get_line()
        return resp, lines

    def send_bytes(self, line):
        """
        Send line to server
        :param line: bytes
        """
        self.sock.sendall(line + CRLF)

    def send_string(self, line):
        """
        Send line to server
        :param line: str
        """
        self.send_bytes(line.encode())

    def short_cmd(self, line):
        """
        Send command
        Returns singleline response
        :param line: str
        """
        self.send_string(line)
        return self.get_resp()

    def long_cmd(self, line):
        """
        Send command
        Returns multiline response
        :param line: str
        """
        self.send_string(line)
        return self.get_long_resp()

    def user(self, user):
        """
        USER command
        :param user: str
        """
        return self.short_cmd('USER %s' % user)

    def pass_(self, pswd):
        """
        PASS command
        :param pswd: str
        """
        return self.short_cmd('PASS %s' % pswd)

    def stat(self):
        """STAT command"""
        return self.short_cmd('STAT')

    def list_(self):
        """LIST command"""
        return self.long_cmd('LIST')

    def retr(self, which):
        """
        RETR command
        :param which: has __str__
        """
        return self.long_cmd('RETR %s' % which)

    def noop(self):
        """NOOP command"""
        return self.short_cmd('NOOP')

    def close(self):
        """Closes the socket"""
        try:
            file = self.file
            self.file = None
            if file is not None:
                file.close()
        finally:
            sock = self.sock
            self.sock = None
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError as e:
                    if e.errno != e.errno.ENOTCONN:
                        return
                finally:
                    sock.close()

    def quit(self):
        """Closes the connection"""
        resp = self.short_cmd('QUIT')
        self.close()
        return resp


class Mail:
    def __init__(self, message):
        """
        :type message: bytes
        """
        self.message = email.message_from_bytes(message)

    def get_headers(self, *headers):
        """
        Yields decoded headers
        :type headers: str
        """
        for header in headers:
            header = self.get_decoded_header(header)
            if header is not None:
                yield header

    def get_decoded_header(self, header):
        """
        Returns decoded header
        :param header: str
        """
        mail_header = self.message.get(header)
        if mail_header:
            return header, \
                   ''.join(text.decode(enc or 'utf-8')
                           if isinstance(text, bytes) else text
                           for text, enc
                           in email.header.decode_header(mail_header))

    def get_message(self, message=None):
        """
        Returns decoded message
        :param message: email.message.Message
        """
        if message is None:
            message = self.message
        content_maintype = message.get_content_maintype()
        if content_maintype == 'multipart':
            return '\n'.join(self.get_message(msg_part)
                             for msg_part in message.get_payload())
        payload = message.get_payload()
        encoding = message.get('Content-Transfer-Encoding')
        charset = message.get_content_charset() or 'utf-8'
        if encoding == 'base64':
            return base64.b64decode(payload).decode(charset)
        elif encoding == 'quoted-printable':
            return quopri.decodestring(payload).decode(charset)
        else:
            return payload


def connect():
    """
    Return pop3 connection;
    Verifies whether email address
    and password are correct
    """
    email_address = input('Input your email:\n')
    password = getpass.getpass('Input your password:\n')

    address_parts = email_address.split('@')
    if len(address_parts) != 2 or '.' not in address_parts[-1]:
        print('Email address is not correct')
        return None

    domain = address_parts[-1]
    if domain not in MAIL_LIST:
        print('This mail server is not supporting yet')
        return None

    try:
        connection = Pop3(*MAIL_LIST[domain])
        connection.user(email_address)
        connection.pass_(password)
        return connection
    except ConnectionError as e:
        print(e)


def get_mail_number(user_input, msg_count):
    """
    Checks whether user_input is correct;
    Returns int(user_input) if it is else None
    :param user_input: str
    :param msg_count: int
    """
    try:
        mail_number = int(user_input)
    except ValueError:
        print('You should input int value')
        return None
    if mail_number > msg_count or mail_number <= 0:
        print('You should input the number ' +
              'below %d and above zero' % msg_count)
        return None
    return mail_number


def main():
    connection = connect()
    while connection is None:
        connection = connect()

    print('Connected.')
    msg_count = int(connection.stat().decode().split()[1])
    print('You have %d message(s)' % msg_count)

    while True:
        user_input = input('Which message do you want to read? (quit)\n' +
                           '=' * 50 + '\n')

        if user_input == 'quit':
            break

        mail_number = get_mail_number(user_input, msg_count)

        if mail_number is None:
            continue

        mail = Mail(b'\n'.join(connection.retr(mail_number)[1]))

        print('=' * 50)
        for header in mail.get_headers('Date', 'From', 'To', 'Subject'):
            print(header[0] + ':')
            print('\t' + header[1])
        print('Message:')
        for msg_line in mail.get_message().split('\n'):
            print('\t' + msg_line)
        print('=' * 50)

    connection.quit()


if __name__ == '__main__':
    main()
