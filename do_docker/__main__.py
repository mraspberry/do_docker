#!python3

import argparse
import os
import time
import digitalocean


def _get_token():
    with open(os.path.join(os.path.dirname(__file__), ".token")) as fd:
        return fd.read().strip()


def _wait_for_running(droplet):
    done = False
    time.sleep(1)
    while not done:
        for act in droplet.get_actions():
            act.load()
            if act.status.lower() == "completed":
                done = True
                break
        else:
            time.sleep(1)
    droplet.load()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("startup", "shutdown"), help="Command to run"
    )
    args = parser.parse_args()
    token = _get_token()
    manager = digitalocean.Manager(token=token)
    tname = "dock_remote"
    if args.command == "startup":
        tag = digitalocean.Tag(token=token, name=tname)
        tag.create()
        keys = manager.get_all_sshkeys()
        droplet = digitalocean.Droplet(
            token=token,
            name="do-docker",
            image="docker-18-04",
            size_slug="g-2vcpu-8gb",
            ssh_keys=keys,
            region="nyc3",
            backup=False,
        )
        droplet.create()
        _wait_for_running(droplet)
        tag.add_droplets([droplet.id])
        while droplet.ip_address is None:
            time.sleep(1)
        print(droplet.id, droplet.ip_address)
    else:
        for droplet in manager.get_all_droplets(tag_name=tname):
            print("Destroying droplet", droplet.id)
            droplet.destroy()


if __name__ == "__main__":
    main()
