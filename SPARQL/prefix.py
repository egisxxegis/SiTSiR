import urllib.parse


def extract_prefix(prefix: str) -> str:
    if prefix.startswith("<") and prefix.endswith(">"):
        return prefix[1:-1]
    return prefix


class Prefix:
    def __init__(self, name: str, prefix_as_declared: str):
        self.raw = prefix_as_declared
        self.url = extract_prefix(self.raw)
        self.urlEncoded = urllib.parse.quote_plus(self.url)
        self.name = name

    def translate(self, prefixed_str: str) -> str:
        if prefixed_str.startswith(self.name):
            return prefixed_str.replace(self.name, self.url, 1)
        raise Exception(f"String '{prefixed_str}' has no prefix '{self.name}'")


def the_prefix(prefix) -> Prefix:
    return prefix
