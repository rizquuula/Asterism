"""Models endpoint."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends

from asterism.config import Config

from ..dependencies import get_config
from ..models import ModelInfo, ModelsListResponse

router = APIRouter()


@router.get("/models")
async def list_models(
    config: Annotated[Config, Depends(get_config)],
) -> ModelsListResponse:
    """List available models.

    Returns all configured models from the provider configuration.

    Args:
        config: Configuration instance

    Returns:
        List of available models
    """
    models: list[ModelInfo] = []

    # Add default model
    default_model = f"asterism/{config.data.agent.name}"
    models.append(
        ModelInfo(
            id=default_model,
            created=int(time.time()),
            owned_by="asterism",
            root=default_model,
        )
    )

    return ModelsListResponse(data=models)
