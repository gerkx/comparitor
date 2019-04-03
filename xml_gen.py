from yattag import Doc, indent

doc, tag, text = Doc().tagtext()

with tag('media'):
    with tag("video"):
        with tag("format"):
            text("boop")

print(indent(doc.getvalue()))
