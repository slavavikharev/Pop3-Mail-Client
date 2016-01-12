from dir import Dir
import os
import sys
import email
import base64
import quopri


class Mail:
    def __init__(self, message, attachments=False, messages=False):
        """
        :type message: bytes
        """
        self.raw = message
        self.message = email.message_from_bytes(self.raw)
        self.attachments = attachments
        self.dir = None
        if messages:
            self.dir = Dir.make_unique_dir()
            self.message_to_file()

    def message_to_file(self):
        try:
            path = os.path.join(self.dir, 'message.msg')
            with open(path, 'wb') as f:
                f.write(self.raw)
        except IOError:
            sys.stderr.write('Cannot write message to file')

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

        payload = message.get_payload()
        encoding = message.get('Content-Transfer-Encoding', '8bit')
        charset = message.get_content_charset() or 'utf-8'

        content_subtype = message.get_content_subtype()

        if message.is_multipart():
            return '\n'.join(self.get_message(msg_part)
                             for msg_part in payload)

        decoded_payload = self.get_decoded_payload(payload, encoding, charset)

        if content_subtype != 'plain':
            if not self.attachments:
                return ''
            self.dir = self.dir or Dir.make_unique_dir()
            filename = message.get_filename() or 'mail.%s' % content_subtype
            file_dir = os.path.join(self.dir, filename)
            try:
                with open(file_dir, 'wb') as f:
                    f.write(decoded_payload)
            except IOError:
                sys.stderr.write('Cannot open %s\n' % file_dir)
                return ''
            return '%s saved' % file_dir

        return decoded_payload.decode(charset)

    @staticmethod
    def get_decoded_payload(payload, encoding, charset):
        """
        Decodes payload with encoding
        Returns decoded in bytes
        :param payload:
        :param encoding:
        :param charset:
        """
        if encoding.lower() == 'base64':
            return base64.b64decode(payload)
        elif encoding.lower() == 'quoted-printable':
            return quopri.decodestring(payload)
        else:
            return payload.encode(charset)
