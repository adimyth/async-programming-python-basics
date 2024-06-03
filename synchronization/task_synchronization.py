import asyncio
from asyncio import Semaphore


async def fetch_data_from_db(sem):
    print("Fetching data from DB...")
    # Simulate time-consuming data fetching
    await asyncio.sleep(1)
    print("Data fetched from DB.")
    # Signal that data is fetched by releasing the semaphore
    sem.release()


async def fetch_data_from_api(sem):
    print("Fetching data from API...")
    # Simulate time-consuming data fetching
    await asyncio.sleep(1)
    print("Data fetched from API.")
    # Signal that data is transformed by releasing the semaphore
    sem.release()


async def transform_data(sem):
    # Here, we are acquiring the semaphore twice to ensure that data is fetched from both DB & API
    await sem.acquire()
    await sem.acquire()
    print("Transforming data...")
    # Simulate data transformation
    await asyncio.sleep(1)
    print("Data transformed.")


async def main():
    # Create a semaphore with initial value 0
    sem = Semaphore(0)

    # Fetching data from DB & API can happen concurrently
    # Transforming data should only happen after data is fetched from both DB & API

    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch_data_from_db(sem))
        tg.create_task(fetch_data_from_api(sem))
        tg.create_task(transform_data(sem))


asyncio.run(main())
