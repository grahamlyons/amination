from datetime import datetime
from subprocess import Popen, PIPE
from boto import ec2
from optparse import OptionParser
import re
from sys import stdout
import json
import os

# Example command:
# sudo aminate -e ec2_chef_linux -B ami-896c96fe --payload-url https://s3-eu-west-1.amazonaws.com/chef-payloads/amination_chef_payload.tar.gz --chef-version 11.10.2 1 -n 'amination-20140623T12_27_00'
#

PROGRAM = "aminate"
ENVIRONMENT = "ec2_chef_debian_linux"
CHEF_VERSION = "11.10.2"
UBUNTU_BASE = "ami-896c96fe"
REGION = "eu-west-1"

def get_option_parser():
    parser = OptionParser()
    parser.add_option("-B", "--base-ami-id", dest="base_ami_id", action="store",
                    default=UBUNTU_BASE,
                    help="The ID of the base AMI to build from.")
    parser.add_option("-c", "--chef-payload-url", action="store",
                    dest="chef_payload",
                    help="don't print status messages to stdout")
    return parser


def get_command(chef_payload, base_ami_id, image_name):
    fake_package = "chef"
    command = (
        PROGRAM,
        "-e",
        ENVIRONMENT,
        "-B",
        base_ami_id,
        "--payload-url",
        chef_payload,
        "--chef-version",
        CHEF_VERSION,
        fake_package,
        "-n",
        image_name
    )
    return [str(a) for a in command]


def get_image_name(chef_payload):
    parts = chef_payload.split("/")
    tarball = parts[-1]
    match = re.match("(\w*)\.tar\.gz", tarball)
    if not match:
        raise SystemExit(1, "Couldn't find tarball name")
    now = datetime.utcnow()
    return "{0}-{1}".format(match.groups()[0], now.strftime("%Y%m%dT%H%M%S"))


def aminate(command):
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    process.wait()
    out, err = process.communicate()

    if process.returncode:
        raise SystemExit(process.returncode, err)
    return 


def get_ami_id(image_name):
    conn = ec2.connect_to_region(REGION)
    images = conn.get_all_images(owners=["self"])
    image = [i for i in images if i.name == "{}-ebs".format(image_name)]
    if not image:
        raise SystemExit(1, "Image not found")
    return image[0].id


def run(chef_payload, base_ami_id, image_name):
    command = get_command(chef_payload, base_ami_id, image_name)
    aminate(command)
    ami_id = get_ami_id(image_name)
    return { 'Data' : { "AmiId": ami_id } }


def main():
    option_parser = get_option_parser()
    (options, args) = option_parser.parse_args()
    chef_payload = options.chef_payload
    base_ami_id = options.base_ami_id
    if not (chef_payload and base_ami_id):
        option_parser.print_help()
        raise SystemExit(1)
    image_name = get_image_name(chef_payload)
    result = run(chef_payload, base_ami_id, image_name)
    stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
