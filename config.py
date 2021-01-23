from typing import List

import environs


env = environs.Env()
env.read_env()

host: str = env.str("HOST", "0.0.0.0")
port: int = env.int("PORT", 8080)

log_level = env.log_level("LOG_LEVEL", "INFO")

clients: List[str] = env.list("CLIENTS")
