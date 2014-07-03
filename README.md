Immutable Deployment Demo Scripts
=================================

This repo contains two [CloudFormation](http://aws.amazon.com/documentation/cloudformation/) templates and a Ruby script which uses the AWS SDK gem.

One template creates the stack for the Amination Factory, which acts as a [CloudFormation CustomResource](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-walkthrough.html) to provide the ID of an AMI.

The second template creates a stack with a loadbalancer and an autoscaling group, which uses the Amination Factory resource to create the AMI from a bundle of Chef recipes stored in a tarball in S3.

The Amination Factory uses the following pieces of open-source software:

 - https://github.com/netflix/aminator
 - https://github.com/aminator-plugins/chef-solo-provisioner (actually using this fork: https://github.com/bmoyles/chef-solo-provisioner)
 - https://github.com/aws/aws-cfn-resource-bridge

Limitations
-----------

This doesn't work with the official base CentOS AMI; the root device is named `/dev/sda` but the block device mapping contains only `/dev/sda1`, which is the partition on that device. This confuses Aminator, tries to find the root device in the device mapping. This was tested with Ubuntu but once that problem is solved this will work with CentOS too.

The Ruby script assumes that the Amination Factory stack is already created (the machine was set up manually).

The Amination Factory machine(s) need to be set up manually with the following procedure:

### Setup

Commands:

 - `apt-get install python-setuptools git -y`
 - `easy_install pip`
 - `pip install git+https://github.com/netflix/aminator`
 - `pip install git+https://github.com/bmoyles/chef-solo-provisioner`
 - `pip install git+https://github.com/aws/aws-cfn-resource-bridge`

The file `amination.py` from this repo needs to be made executable, have `#!/usr/bin/env python` added to the top and moved to `/usr/local/bin/amination`.

The file `environments.yml` needs to be put under `/etc/aminator/`.
The file `cf-resource-bridge.conf` needs to be put under `/etc/cfn/` (the directory may need to be created).
