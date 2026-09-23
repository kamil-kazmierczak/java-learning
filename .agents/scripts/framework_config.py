"""Read the machine configuration and reject invalid settings."""
from jsonschema import Draft202012Validator
from validation_common import ROOT, load_json


def load_config(root=ROOT):
    config = load_json(root / '.agents/config.json')
    schema = load_json(root / '.agents/schemas/config.schema.json')
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(config)
    if config['record_kind'] != 'live':
        raise ValueError('Check selection requires live configuration.')
    return config
