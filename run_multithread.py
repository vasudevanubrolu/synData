import multiprocessing
import subprocess

def work(cmd):
    return subprocess.call(cmd, shell=True, executable="/bin/bash")

if __name__ == '__main__':
    count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=count)

    cmds = []
    num = 1000
    for i in range(count):
        cmds.append('./run.sh {} template_batch6_thread{}_'.format(num, i))
    print(cmds)
    print(pool.map(work, cmds))
