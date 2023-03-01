import os
import json
import requests
import argparse
import concurrent.futures

def download_images(directory):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for entry in os.scandir(directory):
            if entry.name.endswith(".json") and entry.is_file():
                with open(entry.path, encoding="utf8") as f:
                    data = json.load(f)

                small_folder = os.path.join(entry.name.strip(".json"), "small_images")
                large_folder = os.path.join(entry.name.strip(".json"), "large_images")
                os.makedirs(small_folder, exist_ok=True)
                os.makedirs(large_folder, exist_ok=True)

                futures = []
                for item in data:
                    images = item.get("images")
                    if images:
                        small_url = images.get("small")
                        large_url = images.get("large")
                        if small_url:
                            small_filename = os.path.join(small_folder, f"{item['id']}.png")
                            futures.append(executor.submit(download_image, small_url, small_filename))
                        if large_url:
                            large_filename = os.path.join(large_folder, f"{item['id']}_hires.png")
                            futures.append(executor.submit(download_image, large_url, large_filename))
                concurrent.futures.wait(futures)

def download_image(url, filename):
    print("downloading..." + filename)
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from JSON files in a directory.")
    parser.add_argument("directory", help="path to the directory containing the JSON files")
    args = parser.parse_args()

    download_images(args.directory)
