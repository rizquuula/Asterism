"""Config read and update endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from asterism.config import Config

from ..dependencies import get_config

router = APIRouter()


class ProviderInfo(BaseModel):
    type: str
    name: str
    base_url: str | None
    api_key: str | None  # redacted


class ModelsInfo(BaseModel):
    provider: list[ProviderInfo]
    default: str
    fallback: list[str]


class APIInfo(BaseModel):
    host: str
    port: int
    debug: bool
    cors_origins: list[str]


class MCPInfo(BaseModel):
    servers_file: str
    timeout: int


class AgentInfo(BaseModel):
    name: str
    version: str
    description: str


class ConfigResponse(BaseModel):
    agent: AgentInfo
    api: APIInfo
    models: ModelsInfo
    mcp: MCPInfo


class ConfigUpdateRequest(BaseModel):
    key: str
    value: Any


class ConfigUpdateResponse(BaseModel):
    success: bool
    message: str
    key: str


@router.get("/config", response_model=ConfigResponse)
async def get_config_endpoint(
    config: Annotated[Config, Depends(get_config)],
) -> ConfigResponse:
    """Return current configuration (sensitive values redacted).

    API keys are replaced with '***' in the response.
    """
    data = config.data

    providers = [
        ProviderInfo(
            type=p.type,
            name=p.name,
            base_url=p.base_url,
            api_key="***" if p.api_key else None,
        )
        for p in data.models.provider
    ]

    return ConfigResponse(
        agent=AgentInfo(
            name=data.agent.name,
            version=data.agent.version,
            description=data.agent.description,
        ),
        api=APIInfo(
            host=data.api.host,
            port=data.api.port,
            debug=data.api.debug,
            cors_origins=data.api.cors_origins,
        ),
        models=ModelsInfo(
            provider=providers,
            default=data.models.default,
            fallback=data.models.fallback,
        ),
        mcp=MCPInfo(
            servers_file=data.mcp.servers_file,
            timeout=data.mcp.timeout,
        ),
    )


@router.get("/config/schema")
async def get_config_schema(
    config: Annotated[Config, Depends(get_config)],
) -> dict[str, Any]:
    """Return JSON schema for configuration."""
    return config.get_schema()


@router.put("/config", response_model=ConfigUpdateResponse)
async def update_config_endpoint(
    request: ConfigUpdateRequest,
    config: Annotated[Config, Depends(get_config)],
) -> ConfigUpdateResponse:
    """Update a configuration value.

    Use dot notation for nested keys (e.g., "api.port", "models.default").
    Changes are persisted to config.yaml.
    """
    try:
        config.update_value(request.key, request.value)
        return ConfigUpdateResponse(
            success=True,
            message="Configuration updated successfully",
            key=request.key,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
