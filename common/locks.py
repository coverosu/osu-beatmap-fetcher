import asyncio

BEATMAP = asyncio.Lock()
BEATMAP_SEMAPHORE = asyncio.Semaphore(4)
