from __future__ import annotations

import unittest

from play_book_studio.app.server import _parse_multipart_form_data


class ServerRequestParsingTests(unittest.TestCase):
    def test_parse_multipart_form_data_preserves_file_payload_and_filename(self) -> None:
        boundary = "----WebKitFormBoundaryAbC123XYZ"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="title"\r\n\r\n'
            "운영 런북\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="Runbook.PDF"\r\n'
            "Content-Type: application/pdf\r\n\r\n"
        ).encode("utf-8") + b"%PDF-1.4 sample\r\n" + (
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        payload = _parse_multipart_form_data(body, f"multipart/form-data; boundary={boundary}")

        self.assertEqual("운영 런북", payload["title"])
        self.assertEqual(b"%PDF-1.4 sample", payload["file_bytes"])
        self.assertEqual("Runbook.PDF", payload["file_name"])


if __name__ == "__main__":
    unittest.main()
