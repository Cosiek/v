import re

NODE_TYPE_NAME_MATCHER = re.compile(r"<([a-zA-Z0-9]+)([(\/>) ]|$)")


# A void element is one that cannot have any child nodes
VOID_TYPES = {
    "area", "base", "br", "col", "embed",
    "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
}

# Invisible types are ones that are never rendered by browsers
# NOTE: this is not a full list
INVISIBLE_TYPES = {
    "audio", "head", "script", "style", "video",
}

# NOTE: no support for iframe, object and many others


class BaseNode:

    def will_accept(self, buffer: str):
        return False

    def get_text(self):
        return ""


class HTMLNode(BaseNode):

    def __init__(self, buffer: str):
        self.type = get_node_type(buffer)

        self.nodes = []
        self.is_closed = False

    def will_accept(self, buffer: str):
        return not self.is_closed

    def digest(self, buffer: str):
        # check if last node will accept this buffer
        if self.nodes and self.nodes[-1].will_accept(buffer):
            self.nodes[-1].digest(buffer)
        # or is it a closing for this tag
        elif buffer.startswith(f"</{self.type}"):
            self.is_closed = True
        else:
            self.nodes.append(get_new_node(buffer))

    def get_text(self):
        return "\n".join(filter(None, [n.get_text() for n in self.nodes])) if self.is_visible else ""

    @property
    def is_visible(self):
        return self.type not in INVISIBLE_TYPES


class VoidHTMLNode(BaseNode):

    def __init__(self, buffer: str):
        # void nodes can't contain text - no need to care much for them
        self.type = get_node_type(buffer)

    def will_accept(self, buffer: str):
        return False


class TextNode(BaseNode):

    def __init__(self, buffer: str):
        self.type = "text"
        self.content = buffer

    def will_accept(self, buffer: str):
        return not buffer.startswith("<")

    def digest(self, buffer: str):
        self.content += buffer

    def get_text(self):
        return self.content


class CommentNode(BaseNode):

    def __init__(self, buffer: str):
        self.type = "comment"
        self.is_closed = False
        self.digest(buffer)

    def will_accept(self, buffer: str):
        return not self.is_closed

    def digest(self, buffer: str):
        self.is_closed = buffer.endswith("-->")


class TextareaNode(BaseNode):
    """
    textarea tags are a special case, as anything (even valid html) put inside them
    is not parsed and treated as plain text instead.
    """

    def __init__(self, buffer: str):
        self.type = "textarea"
        self.content = ""
        self.is_closed = False

    def will_accept(self, buffer: str):
        return not self.is_closed

    def digest(self, buffer: str):
        self.content += buffer

        self.is_closed = "</textarea" in self.content

    def get_text(self):
        # get rid of closing tag before returning
        return self.content.split("</textarea")[0]


class DoctypeNode(BaseNode):

    def __init__(self, buffer: str):
        self.type = "doctype"

    def will_accept(self, buffer: str):
        return False


class RootNode:

    def __init__(self):
        self.type = "root"
        self.nodes = []

    def digest(self, buffer: str):
        if self.nodes and self.nodes[-1].will_accept(buffer):
            self.nodes[-1].digest(buffer)
        else:
            self.nodes.append(get_new_node(buffer))

    def get_text(self):
        return "\n".join(filter(None, [n.get_text() for n in self.nodes]))


def get_node_type(buffer: str):
    type_mach = NODE_TYPE_NAME_MATCHER.match(buffer)
    if type_mach:
        return type_mach.group(1)
    return None


def get_new_node(buffer: str):
    if not buffer.startswith("<"):
        cls = TextNode
    elif buffer.startswith("<!--"):
        cls = CommentNode
    elif buffer.startswith("<!doctype"):
        cls = DoctypeNode
    elif buffer.startswith("<textarea"):
        cls = TextareaNode
    else:
        # these should be normal html tags
        node_type = get_node_type(buffer)
        if node_type in VOID_TYPES:
            cls = VoidHTMLNode
        elif node_type is None:
            # this doesn't seem to be a proper html tag - treat it as text
            cls = TextNode
        else:
            # this assumes that unknown tags are not void
            cls = HTMLNode

    return cls(buffer)


def parse_html(html: str) -> RootNode:
    root = RootNode()

    buffer = ""
    for letter in html:
        if letter == "<":
            if buffer.strip():  # no whitespace nodes allowed
                root.digest(buffer)
            buffer = "<"
        elif letter == ">":
            root.digest(buffer + letter)
            buffer = ""
        else:
            buffer += letter

    return root