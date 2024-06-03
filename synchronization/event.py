import asyncio


async def reader(event):
    print("Reader waiting for the event to be set")
    await event.wait()
    print("Event is set: Reader can proceed")

async def writer(event):
    print("Writer setting the event")
    await asyncio.sleep(2)
    event.set()
    print("Event is set")


async def main():
    event = asyncio.Event()

    task1 = asyncio.create_task(reader(event))
    task2 = asyncio.create_task(writer(event))

    await asyncio.gather(task1, task2)

asyncio.run(main())