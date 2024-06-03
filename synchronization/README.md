Semaphores are a synchronization primitive used to control access to a common resource by multiple processes in a concurrent system such as an operating system or a multithreaded application. In simpler terms, a semaphore manages access to limited resources by keeping count of the number of available units of that resource.

1. Mutex:
Acts like a lock, allowing only one thread to access a resource at a time.
2. Counting Semaphore:
Allows up to a certain number of threads to access a part of a system or resource simultaneously. The semaphore maintains a set number of permits, and threads must obtain a permit to proceed.

## Mutex - `asyncio.Lock()`

`asyncio.Lock()` is a synchronization primitive that can be used to protect shared resources in a multithreaded environment.

```python

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
        # simulate I/O bound operation
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
```

<span style="color:yellow">Output</span>

```bash
Task 1 is incrementing shared resource
Shared resource before increment: 0
-- waiting for 1 second --
Shared resource after increment: 1
Task 2 is incrementing shared resource
Shared resource before increment: 1
-- waiting for 1 second --
Shared resource after increment: 2
Task 3 is incrementing shared resource
Shared resource before increment: 2
-- waiting for 1 second --
Shared resource after increment: 3
All tasks completed
```

<span style="color:green">Execution Time</span>
~ 3.2 seconds

Here, even though we ran the 3 tasks concurrently, the shared resource was incremented sequentially. This is because we used the `asyncio.Lock()` to protect the shared resource. The `async with lock:` statement acquires the lock, and the critical section is executed. The lock is released when the `async with lock:` block exits.

Since, all the code in the coroutine was part of the critical section, the output was sequential. If we had some I/O bound operations outside the critical section, the tasks would have run concurrently.

For example, if we move the `print(f"Task {id} is incrementing shared resource")` outside the critical section -

<span style="color:yellow">Output</span>

```bash
Task 1 is incrementing shared resource
Shared resource before increment: 0
Task 2 is incrementing shared resource
Task 3 is incrementing shared resource
-- waiting for 1 second --
Shared resource after increment: 1
Shared resource before increment: 1
-- waiting for 1 second --
Shared resource after increment: 2
Shared resource before increment: 2
-- waiting for 1 second --
Shared resource after increment: 3
All tasks completed
```

Here, the 3 tasks are visibly running concurrently (refer the initial print statements), but the shared resource is still being incremented sequentially.


## Counting Semaphores - `asyncio.Semaphore()`
`asyncio.Semaphore()` is a synchronization primitive that can be used to *limit the number of concurrent tasks that can access a shared resource.*

A counting semaphore is initialized with a maximum count value. When a task acquires the semaphore, the count is decremented. When the task releases the semaphore, the count is incremented. If the count reaches 0, the task will block until the semaphore is released by another task.

Example - a printer that can print 3 documents at a time. If more than 3 documents are sent for printing, the extra documents will have to wait until one of the printers is free.

```python
import asyncio

semaphore = asyncio.Semaphore(2)


async def print_document(doc_id):
    async with semaphore:
        print(f"Printing document {doc_id}")
        await asyncio.sleep(2)
        print(f"Document {doc_id} printed")


async def main():
    async with asyncio.TaskGroup() as tg:
        for i in range(1, 5):
            tg.create_task(print_document(i))


asyncio.run(main())
```

<span style="color:yellow">Output</span>

```bash
Printing document 1
Printing document 2
-- waiting for 2 seconds --
Document 1 printed
Document 2 printed
Printing document 3
Printing document 4
-- waiting for 2 seconds --
Document 3 printed
Document 4 printed
```

<span style="color:green">Execution Time</span>
~ 4.2 seconds

Here, the `asyncio.Semaphore(2)` ensures that only 2 tasks can run concurrently. The other tasks will have to wait until one of the slots is free.

Hence, we see that the first 2 documents are printed concurrently, but the next 2 documents are printed only after the first 2 are done.

## Task synchronization
Semaphores can be used to enforce a specific sequence of operations across multiple processes or threads. For instance, you might need to ensure that a certain task (such as initializing a shared resource) is completed before other tasks start.

```python
import asyncio
from asyncio import Semaphore


async def fetch_data_from_db(sem):
    print("Fetching data from DB...")
    # Simulate time-consuming data fetching
    await asyncio.sleep(1)
    print("Data fetched from DB.")
    # Signal that data is fetched by releasing the semaphore
    sem.release()


async def fetch_data_from_api(sem):
    print("Fetching data from API...")
    # Simulate time-consuming data fetching
    await asyncio.sleep(1)
    print("Data fetched from API.")
    # Signal that data is transformed by releasing the semaphore
    sem.release()


async def transform_data(sem):
    # Here, we are acquiring the semaphore twice to ensure that data is fetched from both DB & API
    await sem.acquire()
    await sem.acquire()
    print("Transforming data...")
    # Simulate data transformation
    await asyncio.sleep(1)
    print("Data transformed.")


async def main():
    # Create a semaphore with initial value 0
    sem = Semaphore(0)

    # Fetching data from DB & API can happen concurrently
    # Transforming data should only happen after data is fetched from both DB & API

    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch_data_from_db(sem))
        tg.create_task(fetch_data_from_api(sem))
        tg.create_task(transform_data(sem))


asyncio.run(main())
```

<span style="color:yellow">Output</span>

```bash
Fetching data from DB...
Fetching data from API...
-- wait for 1 second --
Data fetched from API.
Data fetched from DB.
Transforming data...
-- wait for 1 second --
Data transformed.
```

<span style="color:green">Execution Time</span>
~ 2.2 seconds

1. Here, we used a semaphore to ensure that the `transform_data()` coroutine runs only after the data is fetched from both the DB and the API. 
2. The semaphore is initialized with a value of 0, and the `fetch_data_from_db()` and `fetch_data_from_api()` coroutines release the semaphore after fetching the data. 
3. The `transform_data()` coroutine acquires the semaphore twice to ensure that the data is fetched from both sources before proceeding with the transformation.
4. Since, both the `fetch_data_from_db()` and `fetch_data_from_api()` coroutines are running concurrently, the total execution time is less than the sum of the individual execution times. In our case, it takes only 1 seconds to fetch data from both sources as they are running concurrently & each takes 1 second individually.
5. The `transform_data()` coroutine runs only after the data is fetched from both sources, ensuring that the transformation is done on the complete data.



## Event - `asyncio.Event()`
Event is a very low level synchronization primitive that allows one task to signal other tasks that a certain event has occurred. It is a simple mechanism to communicate between tasks.

It's like a flag that can be set or cleared. Tasks can wait for the flag to be set before proceeding.

```python
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
```

<span style="color:yellow">Output</span>

```bash
Reader waiting for the event to be set
Writer setting the event
-- wait for 2 seconds --
Event is set
Event is set: Reader can proceed
```

<span style="color:green">Execution Time</span>
~ 2 seconds

1. Both the `reader()` and `writer()` coroutines started running concurrently.
2. But the `reader()` coroutine waited for the event to be set by the `writer()` coroutine.
3. The `writer()` coroutine set the event after 2 seconds
4. The `reader()` coroutine then proceeded after the event was set.
