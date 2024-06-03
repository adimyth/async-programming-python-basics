import asyncio

shared_resource = 0

lock = asyncio.Lock()


async def increment(id):
    global shared_resource
    async with lock:
        print(f"Task {id} is incrementing shared resource")
        print(f"Shared resource before increment: {shared_resource}")
        # Critical section
        # modify shared resource
        shared_resource += 1
        # simulate I/O bound operation - i.e. we are performing some operation on the shared resource that takes time
        # await will allow other tasks to run, but will not release the lock - so other tasks will wait to acquire the lock & enter the critical section
        await asyncio.sleep(1)
        print(f"Shared resource after increment: {shared_resource}")
        # Critical section ends


async def main():
    async with asyncio.TaskGroup() as tg:
        for i in range(1, 4):
            tg.create_task(increment(i))

    print("All tasks completed")


asyncio.run(main())
