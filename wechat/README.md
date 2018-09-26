# Collection of scripts for CI/CD

## Wechat Mini Program Push

This script aims at auto-pushing mini-program code over to Wechat.

### Requirements

- Wechat IDE CLI
- Slack + bot & token

Also, this script is purely in charge of managing the login + code push to WX. It is not meant to perform the git code pull or any additional other operation like code build or ...

### Usage

```
bash login-push.sh /data/my_project_root v1.0.0 Description
```

Where:
- `/data/my_project_root`: is the path to the root of the project
- `v1.0.0`: is the version we're gonna supply to wechat. Typically it should come from the commit, or tag of the process
- `Description`: is the long description that can be supplied along the upload to WX and will be visible

### Configuration

The script relies on a config file (`login-push.sh.conf`), expected in the same folder as the script.

```
SLACK_BOT_TOKEN=xxx
SLACK_CHANNELS=chan1,chan2
```


