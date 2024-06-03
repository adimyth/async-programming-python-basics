import asyncio


async def fetch_data(id, sleep_time):
    print(f"Fetching data with id: {id}")
    await asyncio.sleep(sleep_time)
    print(f"Data with id: {id} fetched successfully")
    return {"id": id, "data": id}


async def main():
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for i in range(1, 4):
            task = tg.create_task(fetch_data(i, i))
            tasks.append(task)

    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)


asyncio.run(main())
