import codecs
from pathlib import Path
from typing import Optional, Union

from funutil import getLogger
from openapi_python_client import MetaType, generate
from openapi_python_client.config import Config, ConfigFile

logger = getLogger("funapi")


def _process_config(
    *,
    url: Optional[str],
    path: Optional[Path],
    config_path: Optional[Path],
    meta_type: MetaType,
    file_encoding: str,
    overwrite: bool,
    output_path: Optional[Path],
) -> Config:
    source: Union[Path, str]
    if url and not path:
        source = url
    elif path and not url:
        source = path
    elif url and path:
        logger.error("Provide either --url or --path, not both")
        raise Exception
    else:
        logger.error("You must either provide --url or --path")
        raise Exception

    try:
        codecs.getencoder(file_encoding)
    except LookupError as err:
        logger.error(f"Unknown encoding : {file_encoding}")
        raise Exception

    if not config_path:
        config_file = ConfigFile()
    else:
        try:
            config_file = ConfigFile.load_from_path(path=config_path)
        except Exception as err:
            raise Exception

    return Config.from_sources(
        config_file,
        meta_type,
        source,
        file_encoding,
        overwrite,
        output_path=output_path,
    )


def generate_api(
    url: Optional[str] = None,
    path: Optional[Path] = None,
    custom_template_path: Optional[Path] = None,
    meta: MetaType = MetaType.POETRY,
    file_encoding: str = "utf-8",
    config_path: Optional[Path] = None,
    overwrite: bool = False,
    output_path: Optional[Path] = None,
) -> None:
    """Generate a new OpenAPI Client library"""

    config = _process_config(
        url=url,
        path=path,
        config_path=config_path,
        meta_type=meta,
        file_encoding=file_encoding,
        overwrite=overwrite,
        output_path=output_path,
    )
    generate(
        custom_template_path=custom_template_path,
        config=config,
    )
