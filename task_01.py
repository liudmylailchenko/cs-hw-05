import argparse
from aiopath import AsyncPath
import asyncio
import logging
import aioshutil


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def clone_files(path: AsyncPath, dest_folder: AsyncPath):
    try:
        ext = path.suffix[1:] if path.suffix else "no_extension"
        dest_folder = dest_folder / ext
        await dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / path.name

        # Transform path to string for compatibility with shutil
        await aioshutil.copy2(str(path), str(dest_file))
        logging.info(f"Copied file: {path} -> {dest_file}")
    except Exception as e:
        logging.error(f"Error copying file {path}: {e}")


async def read_folder(source_folder: AsyncPath, dest_folder: AsyncPath):
    tasks = []
    async for path in source_folder.rglob("*"):
        if await path.is_file():
            tasks.append(asyncio.create_task(clone_files(path, dest_folder)))
    if tasks:
        await asyncio.gather(*tasks)


async def main():
    parser = argparse.ArgumentParser(
        description="Please enter path to source folder and destination folder."
    )
    parser.add_argument("--source", help="Path to source folder", required=True)
    parser.add_argument(
        "--destination", help="Path to destination folder", required=True
    )
    args = parser.parse_args()

    source = AsyncPath(args.source)
    destination = AsyncPath(args.destination)

    if not await source.exists() or not await source.is_dir():
        logging.error("Source folder does not exist or is not a directory")
        exit(1)

    await read_folder(source, destination)


if __name__ == "__main__":
    asyncio.run(main())
