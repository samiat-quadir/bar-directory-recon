from universal_recon.plugins import social_link_parser as sp


class SocialLinkParserPlugin:
    name = "social_link_parser"

    def fetch(self, **kwargs):
        it = getattr(sp, "iter_profiles", None) or getattr(sp, "fetch", None)
        assert it, "No iter_profiles/fetch in social_link_parser"
        yield from it(**kwargs)

    def transform(self, record):
        f = getattr(sp, "normalize", None) or (lambda x: x)
        return f(record)

    def validate(self, record):
        v = getattr(sp, "is_valid", None) or (lambda x: True)
        return v(record)