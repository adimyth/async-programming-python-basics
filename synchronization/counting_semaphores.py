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
