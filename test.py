import threading
import subprocess

def action(ele):
    subprocess.run(['python', f'./{ele}/download_unzip_clean.py'])


def main():
    threads = []
    elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre"]

    for ele in elements:
        thread = threading.Thread(target=action, args=(ele,))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

main()