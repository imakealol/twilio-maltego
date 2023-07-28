from maltego_trx.decorator_registry import TransformRegistry, TransformSet

registry = TransformRegistry(
        owner="KodamaChameleon",
        author="Kodama Chameleon <contact@kodamachameleon.com>",
        host_url="https://transforms.kodamachameleon.com",
        seed_ids=["Twilio"]
)

# The rest of these attributes are optional

twilio_set = TransformSet("Twilio", "Twilio Transforms")

# metadata
registry.version = "0.1"

# global settings
# from maltego_trx.template_dir.settings import api_key_setting
# registry.global_settings = [api_key_setting]

# transform suffix to indicate datasource
# registry.display_name_suffix = " [ACME]"

# reference OAuth settings
# registry.oauth_settings_id = ['github-oauth']
