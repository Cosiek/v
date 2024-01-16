from pathlib import Path
from unittest import TestCase

from parser import parse_html, get_node_type, get_new_node

TEST_FILES_DIR = Path(__file__).parent / "test_files"


class HTMLParsingTestCase(TestCase):

    @staticmethod
    def get_html(name):
        with open(TEST_FILES_DIR / f"{name}.html") as f:
            return f.read()

    def test_base_html_parsing(self):
        html = self.get_html("base")

        root = parse_html(html)

        self.assertEqual(root.type, "root")
        self.assertEqual(len(root.nodes), 2)

        doctype_node = root.nodes[0]
        self.assertEqual(doctype_node.type, "doctype")

        head_node = root.nodes[1]
        self.assertEqual(head_node.type, "html")

        self.assertEqual(root.get_text(), "Test text.")

    def test_advanced_html_parsing(self):
        html = self.get_html("advanced")

        root = parse_html(html)

        self.assertEqual(root.type, "root")
        self.assertEqual(len(root.nodes), 1)

        expected = (
            "Header\n"
            "Nested paragraph1\n"
            "Nested paragraph2\n"
            "< p>Invalid tag treated as text\n</p>\n"
            "This i a <<<textarea>>>\n"
            "Don't push me!"
        )

        self.assertEqual(expected, root.get_text())

    def test_getting_node_types(self):
        cases = [
            ("p", "<p>"),
            ("p", "<p style=\"xxx\">"),
            ("br", "<br/>"),
            ("br", "<br />"),
            ("div", "<div\nid='whatever'>")
        ]

        for node_type, buffer in cases:
            self.assertEqual(node_type, get_node_type(buffer),
                             f"Error for buffer='{buffer}'")

    def test_getting_new_node_instances(self):
        cases = [
            ("p", "<p>"),
            ("p", "<p style=\"xxx\">"),
            ("br", "<br/>"),
            ("br", "<br />"),
            ("comment", "<!-- THIS IS A COMMENT -->"),
            ("comment", "<!-- THIS IS A \nMULTILINE\n COMMENT -->"),
            ("doctype", "<!doctype html>"),
            ("text", "abc"),
            ("meta", "<meta charset=\"utf-8\" />"),
        ]

        for node_type, buffer in cases:
            node = get_new_node(buffer)
            self.assertIsNotNone(node.type, msg=f"Error for buffer='{buffer}")
            self.assertEqual(node_type, node.type,
                             f"Error for buffer='{buffer}'")
