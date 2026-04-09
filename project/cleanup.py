from db import SessionLocal
import asyncio
from project.logic import del_url

INTERVAL_SECONDS = 3600

async def periodic_cleanup():
    while True:
        async with SessionLocal() as db:
            try:
                deleted_count = await del_url(db)
                print(f"Cleanup worker ran successfully. Deleted {deleted_count} expired links.")
            except Exception as e:
                print(f"Cleanup failed: {e}")

        await asyncio.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(periodic_cleanup())