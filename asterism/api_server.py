#!/usr/bin/env python3
"""Entry point for the Asterism API server."""


import os

import uvicorn

from asterism.config import Config


def main():
    """Run the API server."""

    # Define the target directory
    target_dir = "./workspace"

    # Change the directory if it exists
    if os.path.exists(target_dir):
        os.chdir(target_dir)
        print(f"CWD changed to: {os.getcwd()}")
    else:
        print(f"Warning: {target_dir} not found. Staying in current directory.")

    # Load configuration
    config = Config()

    # Run server
    uvicorn.run(
        "asterism.api:create_api_app",
        host=config.data.api.host,
        port=config.data.api.port,
        reload=config.data.api.debug,
        factory=True,
    )


if __name__ == "__main__":
    main()
