from oxyparser.scraper.scraper import Scraper


def test_it_builds_parsing_instructions_correctly() -> None:
    scraper = Scraper()
    fields_to_xpaths = {
        "name": ["//h1"],
        "surname": ["//h2"],
        "address": ["//p"],
        "age": ["//span"],
        "pets": ["//ul"],
    }

    parsing_instructions = scraper.build_parsing_instructions(fields_to_xpaths)

    expected_parsing_instructions = {
        "name": {
            "_fns": [{"_fn": "xpath_one", "_args": ["//h1"]}],
        },
        "surname": {
            "_fns": [{"_fn": "xpath_one", "_args": ["//h2"]}],
        },
        "address": {
            "_fns": [{"_fn": "xpath_one", "_args": ["//p"]}],
        },
        "age": {
            "_fns": [{"_fn": "xpath_one", "_args": ["//span"]}],
        },
        "pets": {
            "_fns": [{"_fn": "xpath_one", "_args": ["//ul"]}],
        },
    }
    assert parsing_instructions == expected_parsing_instructions
