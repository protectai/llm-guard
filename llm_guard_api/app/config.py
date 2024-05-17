import os
import re
from typing import Any, Dict, List, Literal, Optional

import structlog
import yaml
from pydantic import BaseModel, Field

LOGGER = structlog.getLogger(__name__)

_var_matcher = re.compile(r"\${([^}^{]+)}")
_tag_matcher = re.compile(r"[^$]*\${([^}^{]+)}.*")


class RateLimitConfig(BaseModel):
    enabled: bool = Field(default=False)
    limit: str = Field(default="100/minute")


class AuthConfig(BaseModel):
    type: Literal["http_bearer", "http_basic"] = Field()
    token: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)


class TracingConfig(BaseModel):
    exporter: Literal["otel_http", "console"] = Field(default="console")
    endpoint: Optional[str] = Field(default=None)


class MetricsConfig(BaseModel):
    exporter: Literal["otel_http", "prometheus", "console"] = Field(default="console")
    endpoint: Optional[str] = Field(default=None)


class AppConfig(BaseModel):
    name: Optional[str] = Field(default="LLM Guard API")
    log_level: Optional[str] = Field(default="INFO")
    log_json: Optional[bool] = Field(default=False)
    scan_fail_fast: Optional[bool] = Field(default=False)
    scan_prompt_timeout: Optional[int] = Field(default=10)
    scan_output_timeout: Optional[int] = Field(default=30)
    lazy_load: Optional[bool] = Field(default=False)


class ScannerConfig(BaseModel):
    type: str
    params: Optional[Dict] = Field(default_factory=dict)


class Config(BaseModel):
    input_scanners: List[ScannerConfig] = Field()
    output_scanners: List[ScannerConfig] = Field()
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    auth: Optional[AuthConfig] = Field(default=None)
    app: AppConfig = Field(default_factory=AppConfig)
    tracing: Optional[TracingConfig] = Field(default=None)
    metrics: Optional[MetricsConfig] = Field(default=None)


def _path_constructor(_loader: Any, node: Any):
    def replace_fn(match):
        envparts = f"{match.group(1)}:".split(":")
        return os.environ.get(envparts[0], envparts[1])

    return _var_matcher.sub(replace_fn, node.value)


def load_yaml(filename: str) -> dict:
    yaml.add_implicit_resolver("!envvar", _tag_matcher, None, yaml.SafeLoader)
    yaml.add_constructor("!envvar", _path_constructor, yaml.SafeLoader)
    try:
        with open(filename, "r") as f:
            return yaml.safe_load(f.read())
    except (FileNotFoundError, PermissionError, yaml.YAMLError) as exc:
        LOGGER.error("Error loading YAML file", exception=exc)
        return dict()


def get_config(file_name: str) -> Optional[Config]:
    LOGGER.debug("Loading config file", file_name=file_name)

    conf = load_yaml(file_name)
    if conf == {}:
        return None

    return Config(**conf)
