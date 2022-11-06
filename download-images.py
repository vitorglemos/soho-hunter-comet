import os
import re
import time

import datetime
import aiofiles
import requests
import aiohttp
import asyncio

from os import listdir
from os.path import isfile, join

import shutil

incoming_lasco = "https://sohoftp.nascom.nasa.gov/incoming/lasco/rtmovie_png"
incoming_output_c2 = "/home/vitor/nasa/images/lasco/c2/"
incoming_output_c3 = "/home/vitor/nasa/images/lasco/c3/"


def create_file_management(str_date: str):
    incoming_output_c2_date = os.path.join(incoming_output_c2, str_date)
    incoming_output_c3_date = os.path.join(incoming_output_c3, str_date)
    if not os.path.isdir(incoming_output_c2_date):
        os.mkdir(incoming_output_c2_date)
        print(f"dir created: {incoming_output_c2_date}")
    if not os.path.isdir(incoming_output_c3_date):
        os.mkdir(incoming_output_c3_date)
        print(f"dir created: {incoming_output_c3_date}")

    files_in_c2 = [f for f in listdir(incoming_output_c2_date) if isfile(join(incoming_output_c2_date, f))]
    files_in_c3 = [f for f in listdir(incoming_output_c3_date) if isfile(join(incoming_output_c3_date, f))]
    print(f"Files in c2: {len(files_in_c2)}, Files in c2: {len(files_in_c3)}")

    return files_in_c2, files_in_c3


async def get_images_soho(session):
    async with session.get(incoming_lasco) as response:
        if response.status == 200:
            image_html = await response.read()
            image_html_filter = re.findall('a href="\w+.png"', str(image_html))
            image_html_names = [item.replace("a href=", "").replace('"', "") for item in image_html_filter]

            return image_html_names
        return []


async def main(by_date: str, time: int):
    while True:
        async with aiohttp.ClientSession() as session:
            images = await get_images_soho(session)
            files_in_c2, files_in_c3 = create_file_management(by_date)
            for image in images:
                if re.search(by_date, image):
                    if image not in files_in_c2 and image not in files_in_c3:
                        url_image_soho = f"{incoming_lasco}/{image}"
                        async with session.get(url_image_soho) as response:
                            if re.search("c2.png", image):
                                incoming_output_save = os.path.join(incoming_output_c2, by_date)
                            if re.search("c3.png", image):
                                incoming_output_save = os.path.join(incoming_output_c3, by_date)

                            if response.status == 200:
                                file_handle = await aiofiles.open(os.path.join(incoming_output_save, image), mode='wb')
                                await file_handle.write(await response.read())
                                await file_handle.close()
                        print(f"success: {image}")
        print(f"sleeping by {time} min ...", datetime.datetime.now())
        await asyncio.sleep(60 * time)
