import os
import argparse
import time
import docker

initial_jenkins_setup = False

DEFAULT_DASHBOARD_PORT = 8080
DEFAULT_EXECUTORS_PORT = 50000
DEFAULT_VOLUME_PATH = 'jenkins_home'
DEFAULT_CONTAINER_NAME = 'jenkins'
DEFAULT_IMAGE = 'jenkins/jenkins:lts'


def parse_cli_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--dashboard',
                            type=int,
                            default=DEFAULT_DASHBOARD_PORT,
                            help='Initializes Jenkins dashboard on given port')
    arg_parser.add_argument('-e', '--executors',
                            type=int,
                            default=DEFAULT_EXECUTORS_PORT,
                            help='Allows to connect Jenkins agents on specified port')
    arg_parser.add_argument('-v', '--volume',
                            type=str,
                            default=DEFAULT_VOLUME_PATH,
                            help='Attaches folder to Jenkins container storage directory. Creates one if it does not exist')
    arg_parser.add_argument('-n', '--name',
                            type=str,
                            default=DEFAULT_CONTAINER_NAME,
                            help='Container name')
    arg_parser.add_argument('-q', '--quiet',
                            action='store_true',
                            help='Runs script in quiet mode - Jenkins starts as detached, with no console output')
    arg_parser.add_argument('-i', '--image',
                            type=str,
                            default=DEFAULT_IMAGE,
                            help='Docker image of Jenkins to be started')
    return arg_parser.parse_args()


def get_absolute_path_for_volume(volume):
    global initial_jenkins_setup
    if not os.path.exists(volume):
        os.makedirs(volume)
        initial_jenkins_setup = True
    return os.path.abspath(volume)


def create_jenkins_container(dashboard, executors, volume, name, quiet, image):
    global initial_jenkins_setup

    client = docker.from_env()
    try:
        already_exisiting_container = client.containers.get(name)
        already_exisiting_container.stop()
        already_exisiting_container.remove()
    except docker.errors.NotFound:
        pass

    return client.containers.run(image=image,
                                 detach=True,
                                 ports={8080: dashboard, 50000: executors},
                                 volumes={volume: {'bind': '/var/jenkins_home', 'mode': 'rw'}},
                                 name=name)


def get_jenkins_initial_admin_password(volume):
    password_file_path = os.path.join(volume, os.path.normpath('secrets/initialAdminPassword'))
    while not os.path.exists(password_file_path):
        time.sleep(1)

    password_file_handle = open(password_file_path, "r")
    return password_file_handle.readline().strip()


def get_container_log_stream(jenkins_container):
    return jenkins_container.logs(stream=True)


def print_logs(logs):
    for line in logs:
        print(line.decode('utf-8').strip())


def setup_jenkins(dashboard=8080, executors=50000, volume='jenkins_home', name='jenkins', image='jenkins/jenkins:lts', quiet=True):
    volume = get_absolute_path_for_volume(volume)
    jenkins_container = create_jenkins_container(dashboard=dashboard,
                                                 executors=executors,
                                                 volume=volume,
                                                 name=name,
                                                 quiet=quiet,
                                                 image=image)
    if quiet:
        return get_jenkins_initial_admin_password(volume)
    else:
        return get_container_log_stream(jenkins_container)


if __name__ == '__main__':
    args = parse_cli_arguments()
    setup_result = setup_jenkins(dashboard=args.dashboard,
                                 executors=args.executors,
                                 volume=args.volume,
                                 name=args.name,
                                 image=args.image,
                                 quiet=args.quiet)

    if args.quiet:
        print("Initial admin password is: " + setup_result)
    else:
        print_logs(setup_result)

    exit()
