import os
import time
import yaml
import subprocess

BASES = ("/Users/he.jinkun/PycharmProjects/",)
TIME_FILE = "/Users/he.jinkun/PycharmProjects/time_recorder.yaml"
TARGET_DIR = "/Volumes/hejinkun/python_projects/"

def to_text(msg):
    return msg.decode()


class Backup(object):
    def __init__(self, base_dirs=BASES, target_dir=TARGET_DIR, time_file=TIME_FILE):
        with open(time_file, 'r') as tf:
           self.last_modified_times = yaml.safe_load(tf)
        if self.last_modified_times is None:
            self.last_modified_times = {}
        print('sss', self.last_modified_times)
        self.projects = self.get_need_backup_projects(base_dirs)
        self.target_dir = target_dir
        self.time_file = time_file

    def get_need_backup_projects(self, base_dirs):
        projects = []
        for base in base_dirs:
            for pd in os.listdir(base):
                if os.path.isdir(pd):
                    directory = os.path.join(base, pd)
                    modified_time = time.ctime(max(os.stat(root).st_mtime for root, _, _ in os.walk(directory)))
                    if str(directory) not in self.last_modified_times \
                            or self.last_modified_times[str(directory)] < modified_time:
                        self.last_modified_times[str(directory)] = modified_time
                        projects.append(directory)
        return projects

    def run_command(self, cmd):
        print(cmd)
        process = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate(input=None)
        print("\n".join([to_text(stdout), to_text(stderr)]))
        if process.returncode != 0:
           self.save_modified_times()
           raise Exception('ERROR!')
    
    def save_modified_times(self):
        with open(self.time_file, 'w') as tf:
           yaml.safe_dump(self.last_modified_times, tf)
 
    def backup_projects(self):
        for project in self.projects:
            project_name = os.path.basename(project) + ".tgz"
            compress_cmd = "COPYFILE_DISABLE=1 tar -zcf {0} {1}".format(project_name, project)
            self.run_command(compress_cmd)
            cp_cmd = "cp {0} {1}".format(project_name, self.target_dir)
            self.run_command(cp_cmd)
            rm_cmd = "rm -f {0}".format(project_name)
            self.run_command(rm_cmd)
        self.save_modified_times()
      

backup = Backup()
backup.backup_projects()

