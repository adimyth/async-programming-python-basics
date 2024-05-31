import asyncio


async def main():
    print("Hello")
    await foo()
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(1)


asyncio.run(main())
