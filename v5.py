import asyncio


async def main():
    print("Hello")
    coroutine1 = foo(x="foo", y="bar")
    coroutine2 = foo(x="baz", y="qux")
    await coroutine1
    await coroutine2
    print("World")


async def foo(x: str, y: str):
    print(x)
    await asyncio.sleep(1)
    print(y)


asyncio.run(main())
