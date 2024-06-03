import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    # we have created the task, but we are not awaiting it
    # sleep for 1 second
    await asyncio.sleep(1)
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(10)
    print("bar")


asyncio.run(main())
