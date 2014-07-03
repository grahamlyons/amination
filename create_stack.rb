require 'aws-sdk'

REGION = 'eu-west-1'
BUCKET = 'cf-templates-OrvUA7rZ'.downcase
TEMPLATE = './cf-templates/aminated-loadbalanced-app-in-aws.json'
APPLICATION = 'demoapp'
ENVIRONMENT = 'test'
STACK_NAME = "#{APPLICATION}-#{ENVIRONMENT}"

SNS_TOKEN = 'SNS-TOPIC-NAME'
BASE_HOSTNAME = 'example.com.'

s3 = AWS::S3.new

begin
  bucket = s3.buckets.create(BUCKET)
rescue AWS::S3::Errors::BucketAlreadyOwnedByYou => e
  bucket = s3.buckets[BUCKET]
end

key = TEMPLATE.split('/').last

template = bucket.objects[key]
puts 'Uploading template to bucket'
template.write(Pathname.new(TEMPLATE).realpath)

cfm = AWS::CloudFormation.new(region: REGION)

params = {
  'BaseAmiId' => 'ami-896c96fe',
  'ChefPayloadUrl' => 'https://s3-eu-west-1.amazonaws.com/chef-payloads/demochef.tar.gz',
  'Application' => APPLICATION,
  'Environment' => ENVIRONMENT,
  'AminationFactoryToken' => SNS_TOKEN,
  'BaseHostName' => BASE_HOSTNAME
}

tags = [
  { key: 'Application', value: APPLICATION },
  { key: 'Environment', value: ENVIRONMENT }
]

puts 'Creating stack'
cfm.stacks.create(STACK_NAME, template, :parameters => params, :capabilities => ['CAPABILITY_IAM'], :tags => tags)
