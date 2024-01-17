import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
from unittest import TestCase, mock

from run import main

_CURRENT_DIR = Path(__file__).parent


class ResponseDummy:
    def __init__(self, html):
        self.text = html

    def raise_for_status(self):
        pass


class EndToEndTestCase(TestCase):
    def setUp(self):
        self.fake_datetime = datetime(2020, 1, 1)
        self.expected_output_file_path = _CURRENT_DIR / str(self.fake_datetime)

    def tearDown(self):
        Path.unlink(self.expected_output_file_path, missing_ok=True)

    @mock.patch("run.datetime")
    def test_main(self, datetime_mock):
        html = """
        <html>
          <head>
            <title>Title should be hidden</title>
          </head>
          <body>
            <!-- Can't see me -->
            <p>One two Three Two tHree+three</p>
          </body>
        </html>
        """

        datetime_mock.now.return_value = self.fake_datetime

        with mock.patch("run.requests.get") as requests_mock:
            requests_mock.return_value = ResponseDummy(html)

            # capture stdout to assert right content was printed
            with io.StringIO() as buf:
                with contextlib.redirect_stdout(buf):
                    main("https://example.org")

                printed_out = buf.getvalue()

            # assert printed statements
            self.assertTrue("three: 3" in printed_out)
            self.assertTrue("two: 2" in printed_out)
            self.assertTrue("one: 1" in printed_out)

            self.assertTrue(printed_out.index("three") < printed_out.index("two"))
            self.assertTrue(printed_out.index("two") < printed_out.index("one"))

        # assert output file
        self.assertTrue(self.expected_output_file_path.is_file())
        with open(self.expected_output_file_path, "r") as output_file:
            output = json.load(output_file)

        self.assertEqual([["three", 3], ["two", 2], ["one", 1]], output)
