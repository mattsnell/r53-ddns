# Route 53 Dynamic DNS

Dynamic DNS Services are used by small companies and individuals when they want to publish a service on the Internet, and that service is hosted within an internal or home network.

Home networks commonly use a NAT router to connect to the Internet, the routers can forward ports to services on the internal network and there's value in being able to reference those services by name.  There are many services available to provide free and paid dynamic DNS.  As an alternative, this repository allows you to use a domain you're hosting in [Amazon Route 53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html) for dynamic DNS.

You'll find several assets here, a template to create AWS IAM resources for record management, a python application to keep a Route 53 resource record updated with your assigned IP address, and a Dockerfile to containerize the program.

---

## Setup

* Before running the script, ensure the Route 53 resource record exists

* The guidance and helper scripts assume you're deploying this in a unix-like environment (Linux, macOS)

---

### Create AWS IAM resource for record management

*These steps assume you have [AdministratorAccess](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions.html#jf_administrator) in your AWS account*.

To manage your resource record, you can re-use an existing [AWS Identity and Access Management (IAM)](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) user or create a new one.  

If creating new, the steps below will deploy a user **without login credentials** via a [CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) template.  The user will be able to [ChangeResourceRecordSets](https://docs.aws.amazon.com/Route53/latest/APIReference/API_ChangeResourceRecordSets.html) in a single [hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/route-53-concepts.html#route-53-concepts-hosted-zone).

*Why doesn't the user doesn't have any login credentials?  You should [manage the access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) in whatever way makes sense in your environment.  This repository takes no responsibility for deploying credentials in your AWS account.*

1. Locate the hosted zone ID (e.g. ZCRBOUF1J04GH)

2. [Create a stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html) with [template/iam.yaml](template/iam.yaml) via the [CloudFormation console](https://console.aws.amazon.com/cloudformation)
    * Enter the hosted zone obtained previously as the *"Route53HostedZone"* parameter
    * [Acknowledge](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-template.html#using-iam-capabilities) the "*The following resource(s) require capabilities: [AWS::IAM::ManagedPolicy]*" notification

3. [Create access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) for the user and note the access key ID and secret access key

---

### Script

**_This configuration applies to operating this application locally as a script_**

See [Set up AWS Credentials and Region for Development](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html) to configure your environment with the credentials created above.

Install the required python modules and run the script.  An example is provided below (based on Debian Buster), modify for your environment.

```bash
apt-get install python3-pip -y
pip3 install virtualenv
python3 -m virtualenv --python python3 .venv
source .venv/bin/activate
pip install -r script/requirements.txt
# replace zone id and domain with appropriate values
script/r53-ddns.py --hosted-zone-id ZCRBOUF1J04GH --name home.mydomain.com
```

Assuming all goes well, you can cron the script (ensure you're utilizing the virtual environment you created).

*Note*: You can hard-code the values for the zone (`hosted_zone_id = ''`) and name (`dns_name = ''`) in the [script](script/r53-ddns.py) and omit the command line arguments if desired.

---

### Container

**_This configuration applies to operating this application as a container and assumes that docker is installed and working on your system_**

* [script/r53-ddns.conf](script/r53-ddns.conf) contains required variables passed to the container at run-time.  Configure appropriately, an example is provided below:

```text
# aws credentials
AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# route 53
DNS_NAME="home.mydomain.com"
HOSTED_ZONE_ID="ZCRBOUF1J04GH"
```

* Update [run.sh](run.sh) and provide the absolute path to the `r53-ddns.conf` on your system

* Build the container (with a [helper script](build.sh)):

```bash
./build.sh
```

* Run the container (with a [helper script](run.sh)):

```bash
./run.sh
```

Assuming all goes well, you can cron the [`run.sh`](run.sh) script

---
