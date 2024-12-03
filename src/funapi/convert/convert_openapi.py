import json

import requests
from funfake.headers import fake_header
from funutil import getLogger

logger = getLogger("funapi")


def convert_openapi_v3(
    openapi_filepath_ori="openapi-ori.json", openapi_filepath_v3="openapi-v3.json"
):
    url = "https://converter.swagger.io/api/convert"
    headers = fake_header()
    data = requests.post(
        url, json=json.loads(open(openapi_filepath_ori, "r").read()), headers=headers
    )
    with open(openapi_filepath_v3, "w", encoding="utf-8") as f:
        f.write(json.dumps(data.json(), indent=4, ensure_ascii=False))
    logger.success(f"converted success: {openapi_filepath_v3}")
