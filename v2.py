import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(1)
    print("bar")


asyncio.run(main())
