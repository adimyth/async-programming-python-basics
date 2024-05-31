# Async Programming in Python

1. Golden Rule: **Never block the event loop**
2. Key Takeaway: **There can only be one thing that the event loop is doing at any given time.**
3. Execution: **There will be some additional overhead in running async code & switching between tasks. This will lead to increased time comapred to sync code**

## v1

```python
import asyncio


async def main():
    print("Hello")
    await foo()
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(1)


asyncio.run(main())
```

Even though we have written asynchronous code, this is not actually running asynchronusly. The event loop created using `asyncio.run` is running the `main` function.

Inside the `main` function we await `foo` function. The `foo` function is an asynchronous function that sleeps for 1 second. The `main` function will wait for the `foo` function to complete before printing "World". So, the order is -


<span style="color:yellow">Output</span>

```bash
Hello
foo
-- wait for 1 second --
World
```

<span style="color:red">Execution Time</span>

In all it takes > 1 second to complete the execution. 

> This is no different or better than running the code synchronously as follows -

```python
import time

def main():
    print("Hello")
    foo()
    print("World")


def foo():
    print("foo")
    time.sleep(1)

main()
```

## v2
To actually run the code asynchronously, we need to create a task using `asyncio.create_task`.
```python
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

```

PS - Here, I am not awaiting the task. In such a case, the `main` function will continue executing without waiting for the `foo` function to complete.

🤯 But when you run the program, you get the following output

<span style="color:yellow">Output</span>
```bash
Hello
foo
World
```

<span style="color:red">Execution Time</span>

~200ms


> `bar` is not printed & the program completed in ~200ms.

This happened because the `main` function completed before the `foo` function could complete. The `foo` function was running in the background as a task. When the `main` function completed, the program exited without waiting for the `foo` function to complete.


## v3
To fix this, we need to await the task created using `asyncio.create_task`.

```python
import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    await task
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(1)
    print("bar")


asyncio.run(main())
```

<span style="color:yellow">Output</span>
```bash
Hello
foo
-- wait for 1 second --
bar
World
```

<span style="color:red">Execution Time</span>
~ 1.2 seconds

> The `main` function will wait for the `foo` function to complete before printing "World". The `foo` function will complete in 1 second and then the `main` function will print "World".

😞 But note that it still takes 1.2s to run, so from these examples the benefit of async is not clear at all.

Where async really shines is when you have multiple tasks running concurrently. In the next example, we will run multiple tasks concurrently.

## v4
```python
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
```

Here, we are running **two tasks concurrently**. The `main` function will wait for both tasks to complete before printing "World".

Since, both tasks are running concurrently, the total time taken to complete the program will be the time taken by the longest running task.

<span style="color:yellow">Output</span>
```bash
Hello
foo
baz
-- wait for 1 second --
bar
qux
World
```

<span style="color:red">Execution Time</span>
~ 1.2 seconds


## v5
To better understand the concurrency & how the context switch happens based on the `await` statement as well as the amount of time a blocking function runs for (sleep time in our case), let's look at the following example -

```python
import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    # we have created the task, but we are not awaiting it
    await asyncio.sleep(1)
    print("World")


async def foo():
    print("foo")
    # the function will run for 10 seconds
    await asyncio.sleep(10)
    print("bar")


asyncio.run(main())
```
Things to note here -
1. I am not awaiting the task created using `asyncio.create_task`
2. The `main` function will sleep for 1 second after creating the task

<span style="color:yellow">Output</span>
```bash
Hello
foo
-- wait for 1 second --
World
```

<span style="color:red">Execution Time</span>
~ 1.2 seconds

🤯 `bar` was never printed and the script completed in ~1.2 seconds - why did this happen?

1. `asyncio.run(main())`: starts the `main()` coroutine. This call initializes and starts running the event loop.
2. `print("Hello")`: prints "Hello" to the console.
3. `asyncio.create_task(foo())`: This schedules the `foo()` coroutine to be run by the event loop. <span style="color:orange">***However, it doesn't start executing `foo()` immediately; it merely schedules it to be run as soon as the event loop gets control and decides to start it.***</span>
4. `await asyncio.sleep(1)`: This tells the event loop to pause the execution of the `main()` coroutine for 1 second. <span style="color:orange">***The await keyword here is critical because it tells the event loop that the `main()` coroutine is going to wait for 1 second and that the event loop should take this opportunity to run other tasks/coroutines that are ready to run.***</span> This is our first explicit context switch.
5. `print("foo")`: Since, the only other coroutine is the `task` created previously, the event loop runs the `foo` coroutines & hence "foo" is printed to the console.
6. `await asyncio.sleep(10)`: `foo()` coroutine is now going to wait for 10 seconds. <span style="color:orange">***The `await` keyword tells the event loop that the `foo()` coroutine is going to wait for 10 seconds and that the event loop should take this opportunity to run other tasks/coroutines that are ready to run.***</span> This is our second explicit context switch.
7. *Back to `main()`*:  Since foo() is now sleeping and the only other coroutine is main(), which itself was sleeping for 1 second, the event loop returns to `main()` once the 1-second sleep completes.
8. `print("World")`: After the 1-second sleep, "World" is printed to the console. This happens before foo() completes its 10-second sleep.
9. *End of `main()`*: At this point, `main()` has finished executing all its code. However, the event loop is still running because `foo()` is still in its sleep.
11. *Event Loop Closes*: Since `main()` was the coroutine called by `asyncio.run()`, the event loop automatically closes when `main()` completes, even if other tasks like `foo()` have not yet completed


**Note** - Here, the context switch happened from `main` to `foo` & the `foo` function ran till it hit the `await asyncio.sleep(10)` statement. This happened without we explicitly awaiting the task we created. The event loop was smart enough to switch the context to the `foo` (the only other coroutine) as soon as it hit the `await asyncio.sleep(1)` statement in the `main` function.

> 🤔 It would be very interesting to see what would happen if there were 2 tasks & we awaited one of the tasks & didn't await the other.

## v6
Now what would happen if we await the task created using `asyncio.create_task`?

```python
import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    await task
    # sleep for 1 second
    await asyncio.sleep(1)
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(10)
    print("bar")


asyncio.run(main())
```

<span style="color:yellow">Output</span>
```bash
Hello
foo
-- wait for 10 seconds --
bar
-- wait for 1 second --
World
```

<span style="color:red">Execution Time</span>
~ 11.2 seconds

This is on expected lines. The execution order will be as follows -
1. `main()` coroutine starts
2. `print("Hello")` is executed
3. `asyncio.create_task(foo())` is executed. This schedules the `foo()` coroutine to be run by the event loop but doesn't start executing it immediately. The event loop will start executing `foo()` as soon as it gets control.
4. `await task` pauses the execution of the `main()` coroutine until the `foo()` coroutine completes. This is our 1️⃣ explicit context switch.
5. `print("foo")` is executed. Since `foo()` is the only other coroutine, the event loop runs `foo()` and prints "foo" to the console.
6. `await asyncio.sleep(10)` pauses the execution of the `foo()` coroutine for 10 seconds. This is our 2️⃣ explicit context switch.
7. `print("bar")` is executed after the 10-second sleep. Now, the `foo()` coroutine has completed. The event loop returns to the `main()` coroutine.
8. `await asyncio.sleep(1)` pauses the execution of the `main()` coroutine for 1 second. This is our 3️⃣ explicit context switch.
9. `print("World")` is executed after the 1-second sleep.
10. The `main()` coroutine has completed, and the event loop closes.


## v7
For the final variation, we will just switch the amount of time the `foo` function sleeps for and the amount of time the `main` function sleeps for.

```python
import asyncio


async def main():
    print("Hello")
    task = asyncio.create_task(foo())
    await task
    await asyncio.sleep(10)
    print("World")


async def foo():
    print("foo")
    await asyncio.sleep(1)
    print("bar")


asyncio.run(main())
```

<span style="color:yellow">Output</span>
```bash
Hello
foo
-- wait for 1 second --
bar
-- wait for 10 seconds --
World
```

<span style="color:red">Execution Time</span>
~ 11.2 seconds

The execution order will be as follows -
1. `asyncio.run(main())`: starts the `main()` coroutine. This call initializes and starts running the event loop.
2. `print("Hello")`: prints "Hello" to the console.
3. `asyncio.create_task(foo())`: This schedules the `foo()` coroutine to be run by the event loop. <span style="color:orange">***However, it doesn't start executing `foo()` immediately; it merely schedules it to be run as soon as the event loop gets control and decides to start it.***</span>
4. `await task`: pauses the execution of the `main()` coroutine until the `foo()` coroutine completes. This is our 1️⃣ explicit context switch.
5. `print("foo")`: is executed. Since `foo()` is the only other coroutine, the event loop runs `foo()` and prints "foo" to the console.
6. `await asyncio.sleep(1)`: pauses the execution of the `foo()` coroutine for 1 second. This is our 2️⃣ explicit context switch.
7. `print("bar")`: is executed after the 1-second sleep.
8. *Back to `main()`*: The `foo()` coroutine has completed. The event loop returns to the `main()` coroutine. <span style="color:orange">*This is an implicit context switch.*</span>
9. `await asyncio.sleep(10)`: pauses the execution of the `main()` coroutine for 10 seconds. This is our 3️⃣ explicit context switch.
10. `print("World")`: is executed after the 10-second sleep.



## v8
The most complex example - 

```python
import asyncio


async def main():
    print("Hello")
    task1 = asyncio.create_task(foo(x="foo", y="bar", sleep_time=1))
    task2 = asyncio.create_task(foo(x="baz", y="qux", sleep_time=2))
    await task1
    await asyncio.sleep(0.5)
    print("World")


async def foo(x: str, y: str, sleep_time: int):
    print(x)
    await asyncio.sleep(sleep_time)
    print(y)


asyncio.run(main())
```

<span style="color:yellow">🤯 Output</span>
```bash
Hello
foo
baz
-- wait for 1 second --
bar
World
```

<span style="color:red">Execution Time</span>
~ 1.27 seconds

The execution order will be as follows -
1. `asyncio.run(main())`: Starts the main() coroutine and initializes the event loop.
2. `print("Hello")`: Prints "Hello".
3. Task Creation:
   1. `task1 = asyncio.create_task(foo(x="foo", y="bar", sleep_time=1))`: Schedules `foo()` to be run with `x="foo", y="bar", sleep_time=1`.
   2. `task2 = asyncio.create_task(foo(x="baz", y="qux", sleep_time=2))`: Schedules another instance of `foo()` to be run *concurrently* with `x="baz", y="qux", sleep_time=2`.
4. Immediate Execution of Both Tasks:
   1. `task1` starts and prints "foo".
   2. Almost simultaneously, `task2` starts and prints "baz".
5. Context Switch Due to await in Tasks: Both tasks enter their respective sleep calls (`await asyncio.sleep(...)`). `task1` will sleep for 1 second, and `task2` will sleep for 2 seconds.
6. `await task1` in `main`: 
   1. The `main()` coroutine now **explicitly waits** for `task1` to complete. <span style="color:orange">This isn't a context switch to another task but rather waiting for a particular task (task1) to finish.</span>
   2. The event loop waits until task1's sleep of 1 second is complete. During this time, task2 is still sleeping.
7. `task1` completes:
   1. After 1 second, `task1` resumes and prints "bar".
   2. `task1` completes and `main()` resumes immediately after `task1`.
8. `main()` Continues After `task1`: After `task1` finishes, `main()` executes `await asyncio.sleep(0.5)`. <span style="color:orange">This introduces another context switch as main() now waits for 0.5 seconds. But this time, it's not waiting for a specific task to complete.</span>
9. `print("World")`: After the 0.5-second sleep, `main()` prints "World".


🔥 Note, that when the event loop faced `await asyncio.sleep(0.5)` in `main` function, it did context switch & ran the `task2` function. But since the `task2` function was still sleeping, the event loop switched back to the `main` function after 0.5 seconds & printed "World".

🔥 🔥 Had the `main` function be sleeping for `5` seconds, instead of `0.5` seconds, `task2` would have ran to completion without explicitly needing to await for it.
So, basically, the context switch happens whenever the event loop faces an `await` statement. The outpu then looks like -

<span style="color:yellow">Output</span>
```bash
Hello
foo
baz
-- wait for 1 second --
bar
-- wait for another 1 second --
-- task2 already waited 1 second before (remeber task1 & task2 started concurrently) --
qux
-- wait for 5 seconds --
World
```

The execution time will be ~ 6.2 seconds.


**NOTE**: If the `await` statement is in the `main` function, the event loop will switch to the next task in the queue. If the `await` statement is in a task, the event loop will switch to the next task in the queue.