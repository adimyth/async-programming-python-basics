import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    await task
    await asyncio.sleep(1)
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(10)
    print("bar")


asyncio.run(main())
