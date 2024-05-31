import asyncio


async def main():
    print("Hello")
    task1 = asyncio.create_task(foo(x="foo", y="bar"))
    task2 = asyncio.create_task(foo(x="baz", y="qux"))
    await task1
    await task2
    print("World")


async def foo(x: str, y: str):
    print(x)
    await asyncio.sleep(1)
    print(y)


asyncio.run(main())
