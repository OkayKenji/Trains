import threading
import subprocess

def action(ele):
    subprocess.run(['python', f'./{ele}/download_unzip_clean.py'])
    print(f'Done: {ele}')


def main():
    threads = []
    elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta"]

    for ele in elements:
        thread = threading.Thread(target=action, args=(ele,))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

main()