#!/usr/bin/env python

# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example of using the Compute Engine API to create and delete instances.

Creates a new compute engine instance and uses it to apply a caption to
an image.

    https://cloud.google.com/compute/docs/tutorials/python-guide

For more information, see the README.md under /compute.
"""

import argparse
import os
import time

import googleapiclient.discovery
from six.moves import input


# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items']
# [END list_instances]


# [START create_instance]
def create_instance(compute, project, zone, name, instance_type):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']
    print source_disk_image
    # Configure the machine
    machine_type = "zones/%s/machineTypes/%s" % (zone , instance_type)
    print machine_type
    startup_script = open(os.path.join(os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
    
    print startup_script
    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                    'diskSizeGb': '10'
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }
            ]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance]


# [START delete_instance]
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()
# [END delete_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]



# [START run]


def swarmmain(project, zone, instance_name, instance_type):
    compute = googleapiclient.discovery.build('compute', 'v1')

    print('Creating instance.')

    operation = create_instance(compute, project, zone, instance_name, instance_type)
    wait_for_operation(compute, project, zone, operation['name'])

    instances = list_instances(compute, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(' - ' + instance['name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('selfhealing-216620', help='Your Google Cloud project ID.')
    parser.add_argument('self-healing-bucket', help='Your Google Cloud Storage bucket name.')
    parser.add_argument('--zone', default='europe-west2-b',help='Compute Engine zone to deploy to.')
    parser.add_argument('--name', default='demo-instance', help='New instance name.')
    compute = googleapiclient.discovery.build('compute', 'v1')
    #args = parser.parse_args()
    #instances = list_instances(compute, 'selfhealing-216620', 'europe-west2-b')
    swarmmain('selfhealing-216620', 'europe-west2-b', 'swarm-5', 'n1-standard-1')
    #sleep(30)
    #delete_instance(compute,'selfhealing-216620', 'europe-west2-b', 'swarm-4' )
    #main(args.project_id, args.bucket_name, args.zone, args.name)
# [END run]