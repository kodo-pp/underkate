from underkate.python_functions import sleep


async def main(*, script, **kwargs):
    await sleep(script, 2.0)
    print('Hello')
    await sleep(script, 2.0)
    print('again')
