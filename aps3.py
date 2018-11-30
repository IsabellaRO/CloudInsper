import boto3, os, errno
from botocore.exceptions import ClientError
#print(boto3.__version__)

# Referência: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-key-pairs.html

ec2 = boto3.client('ec2', region_name='us-east-1')
ec2r = boto3.resource('ec2')
#ec2.instances.filter(TagSpecifications={'ResourceType': 'instance', 'Tags': [{'Key': 'Owner', 'Value': 'Isabella'}]}).stop()
#ec2.instances.filter(TagSpecifications={'ResourceType': 'instance', 'Tags': [{'Key': 'Owner', 'Value': 'Isabella'}]}).terminate()

reservations = ec2r.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in reservations:
    if instance.tags is None:
        continue
    for tag in instance.tags:
        if tag['Value'] == 'Isabella':
            instance.stop()
            instance.terminate()

keypair = ec2.delete_key_pair(KeyName='Key_pair')
print("Key pair apagada")
#ler o conteudo da ~/.ssh/id_rsa.pub
keypair_file = open("/home/isabella/.ssh/id_rsa.pub", 'r')
Key_pair = keypair_file.read()
keypair = ec2.import_key_pair(
    KeyName='Key_pair',
    PublicKeyMaterial= Key_pair
)
print("Key pair importada")

# Referência: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-security-group.html
response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

# Delete security group
try:
    response = ec2.delete_security_group(GroupName='APS')
    print('Security Group Deleted')
except ClientError as e:
    print(e)

# Create security group
try:
    response = ec2.create_security_group(GroupName='APS',
                                         Description='Nenhuma',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 5000,
             'ToPort': 5000,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)

# Referência: https://stackoverflow.com/questions/32863768/how-to-create-an-ec2-instance-using-boto3
# Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0ac019f4fcb7cb7e6 (64-bit x86) / ami-01ac7d9c1179d7b74 (64-bit Arm)
instance = ec2.run_instances(
    ImageId='ami-0ac019f4fcb7cb7e6',
    InstanceType='t2.micro',
    KeyName='Key_pair',
    MaxCount=1,
    MinCount=1,
    SecurityGroups=[
        'APS'
    ],
    UserData='''#!/bin/sh
    cd /
    git clone https://github.com/IsabellaRO/CloudInsper/
    ./install.sh
    ''',
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Owner',
                    'Value': 'Isabella'
                }
            ]
        }
    ]
)