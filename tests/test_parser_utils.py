from oxyparser.parser.ai_parser import AIParser


def test_it_modifies_class_selector_correctly() -> None:
    parser = AIParser()
    selector = "//div[@class='some-class']"
    modified_selector = parser.modify_class_selector(selector)

    assert modified_selector == "//div[contains(@class, 'some-class')]"


def test_it_splits_body_into_parts_correctly() -> None:
    parser = AIParser()
    html = "<html><body><p>Some text</p><p>Some more text</p></body></html>" * 1000
    html_split_into_parts = parser.split_body_into_parts(html)

    assert len(html_split_into_parts) == 7


def test_it_parses_html_correctly() -> None:
    parser = AIParser()
    html = "<html><body><h1>John</h1><h2>Smith</h2><p>Svitrigailos st.</p><span>2 years old</span></body></html>"
    fields_to_selectors = {
        "name": ["//h1"],
        "surname": ["//h2"],
        "address": ["//p"],
        "age": ["//span"],
    }
    parsed_item = parser.parse_html(fields_to_selectors, [html])

    assert parsed_item == {
        "name": ["John"],
        "surname": ["Smith"],
        "address": ["Svitrigailos st."],
        "age": ["2 years old"],
    }
