import socket
import ssl

CR = b'\r'
LF = b'\n'
CRLF = CR + LF


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
                except OSError:
                    return
                finally:
                    sock.close()

    def quit(self):
        """Closes the connection"""
        resp = self.short_cmd('QUIT')
        self.close()
        return resp
