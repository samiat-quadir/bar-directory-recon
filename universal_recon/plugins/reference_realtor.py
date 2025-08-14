
class RealtorPlugin:
    name = "realtor_reference"

    def fetch(self, **kwargs):
        yield {"source": "realtor", "raw": {}}

    def transform(self, record):
        return record

    def validate(self, record):
        return True
