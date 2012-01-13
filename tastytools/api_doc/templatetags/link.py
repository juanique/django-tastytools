from django import template
import settings

register = template.Library()

class LinkNode(template.Node):
    def __init__(self, file_type, file_path):
        self.file_type = file_type
        if not file_path.endswith(file_type) and file_type != "img":
            file_path = "%s.%s" % (file_path, file_type)
        self.file_path = file_path

    def render(self, context):
        if self.file_type == 'js':
            tag = "<script type='text/javascript' src='%sjs/%s'></script>" % (settings.STATIC_URL, self.file_path)
        if self.file_type == 'css':
            tag = "<link rel='stylesheet' type='text/css' href='%scss/%s'>" % (settings.STATIC_URL, self.file_path)
        if self.file_type == 'img':
            tag = "<img src='%simg/%s'/>" % (settings.STATIC_URL, self.file_path)

        return tag


def link_tag(parser, token):
    (link_type, link_file) = tuple(token.split_contents()[1].split(":"))
    return LinkNode(link_type, link_file)

register.tag('link',link_tag)

print settings.STATIC_URL
