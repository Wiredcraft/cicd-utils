# Collection of scripts for CI/CD

## Wechat Mini Program Push

This script aims at auto-pushing mini-program code over to Wechat.

### Requirements

- Wechat IDE CLI
- Slack + bot & token

Also, this script is purely in charge of managing the login + code push to WX. It is not meant to perform the git code pull or any additional other operation like code build or ...

### Dependencies

```
pip install requests
```

### Configuration

The configuration relies on Env vars

```
# The token used to connect to Slack 
export SLACK_BOT_TOKEN=xxx

# The list of Slack channels (comma separated) to send the QR code to
export SLACK_CHANNELS=chan1,chan2
```

### Usage

```
# Usage: 
#  ./login_push.py [version] [workspace] [description]
#      version:     the version to upload to Wechat
#      workspace:   the path of the Mini Program code base
#      description: description of the release

./login_push.py v1.0.0 /data/my_project_root Description
```

Where:
- `v1.0.0`: is the version we're gonna supply to wechat. Typically it should come from the commit, or tag of the process
- `/data/my_project_root`: is the path to the root of the project
- `Description`: is the long description that can be supplied along the upload to WX and will be visible



