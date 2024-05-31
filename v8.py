import asyncio


async def main():
    print("Hello")
    task1 = asyncio.create_task(foo(x="foo", y="bar", sleep_time=1))
    task2 = asyncio.create_task(foo(x="baz", y="qux", sleep_time=2))
    await task1
    # await asyncio.sleep(0.5)
    # Try changing the sleep time to 5 seconds and see what happens
    await asyncio.sleep(5)
    print("World")


async def foo(x: str, y: str, sleep_time: int):
    print(x)
    await asyncio.sleep(sleep_time)
    print(y)


asyncio.run(main())
