import ossapi

import config

v1 = ossapi.Ossapi(
    key=config.osu_api_key,
)
v2 = ossapi.OssapiV2(
    client_id=config.client_id,
    client_secret=config.client_secret,
)
