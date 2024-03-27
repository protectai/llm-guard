import argparse

import uvicorn

from .app import create_app


def run_uvicorn():
    parser = argparse.ArgumentParser(description="LLM Guard API")
    parser.add_argument("config", type=str, help="Path to the configuration file")
    parser.add_argument("--port", type=int, help="Port to run the server on", default=8000)
    args = parser.parse_args()
    scanners_config_file = args.config

    uvicorn.run(
        create_app(scanners_config_file),
        host="0.0.0.0",
        port=args.port,
        server_header=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
        timeout_keep_alive=2,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Guard API")
    parser.add_argument("config", type=str, help="Path to the configuration file")
    args = parser.parse_args()
    scanners_config_file = args.config

    run_uvicorn()
