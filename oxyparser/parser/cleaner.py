from lxml import etree, html
from lxml.html.clean import Cleaner


def clean_empty_tags(html_doc: str) -> str:
    tree = html.fromstring(html_doc)

    context = etree.iterwalk(tree)
    for _, elem in context:
        parent = elem.getparent()
        if remove_empty_tags(elem):
            parent.remove(elem)

    cleaned_html = html.tostring(tree)
    return cleaned_html.decode("utf-8")


def remove_empty_tags(element: etree.ElementBase) -> bool:
    if element.text:
        return False
    return all((remove_empty_tags(c) for c in element.iterchildren()))


def extract_body_from_html(full_html: str) -> str | None:
    tree = html.fromstring(full_html)
    body = tree.xpath("//body")
    if not body:
        return None
    return html.tostring(body[0]).decode()


def clean_line_breaks(html_doc: str) -> str:
    html_doc = "".join(html_doc.splitlines())
    return html_doc


def clean_html(full_html: str) -> str | None:
    extracted_body = extract_body_from_html(full_html)
    if not extracted_body:
        return None

    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True
    cleaner.remove_tags = ["a"]
    cleaner.kill_tags = ["nav", "svg", "footer", "header", "table", "img", "noscript"]

    cleaned_html = cleaner.clean_html(extracted_body)
    cleaned_html = clean_empty_tags(cleaned_html)
    cleaned_html = clean_line_breaks(cleaned_html)

    return cleaned_html
