#!/usr/bin/env python
# -*- coding: utf-8 -*-

##################
#
# Simple Login and Push to Wechat Mini-program
# Created by Song in Wiredcraft
#
##################
#
# ChangeLog
# 20180928 Song Initial Creation
#
##################
#
# Usage:
#   export SLACK_BOT_TOKEN=""
#   export SLACK_CHANNELS=cicd
#   python login_push.py version project_root description
#
##################

import base64
import os
import re
import requests
import subprocess
import sys


SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNELS = os.environ.get("SLACK_CHANNELS", "")

RETRY_LOGIN = os.environ.get("RETRY_LOGIN", "3")
RETRY_PUSH = os.environ.get("RETRY_PUSH", "3")

# Document: https://api.slack.com/methods/files.upload
SLACK_UPLOAD_URL = "https://slack.com/api/files.upload"
CMD_CLI = "/Applications/wechatwebdevtools.app/Contents/Resources/app.nw/bin/cli"


def decode_image(base64_text, output_file=None):
    img_data = base64.b64decode(re.sub('^data:image/.+;base64,', '', base64_text))
    if output_file:
        with open(output_file, "wb") as file:
            file.write(img_data)
    return img_data


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def login(retry=3):
    for line in execute([
        CMD_CLI,
        "-l",
        "--login-qr-output base64"]
    ):
        if line.startswith("data:image/jpeg;base64"):
            image = decode_image(line)
            result = requests.post(
                SLACK_UPLOAD_URL,
                files={'file': image},
                data={
                    "token": SLACK_BOT_TOKEN,
                    "channels": SLACK_CHANNELS,
                }
            )
            if result.status_code != 200:
                print("Failed to upload the qrcode to slack!")
        elif line.startswith("login success"):
            print("Success")
            return True
        else:
            print(line)

    if retry > 0:
        print("Error: Login Failed. Retrying...")
        return login(retry=retry-1)
    else:
        print("Error: Login Failed.")

    return False


def push(version, project_root, description, retry=3):
    for line in execute([
        CMD_CLI,
        "--upload",
        "{version}@{project_root}".format(version=version, project_root=project_root),
        "--upload-desc",
        "{description}".format(description=description)
    ]):
        if line.startswith("upload success"):
            print("Push Succeeded!")
            return True

        # Looking for line:
        # error: '{"code":40000,"error":"错误 需要重新登录"}',
        if line.strip().startswith("error:") and '"code":40000' in line:
            login(retry=int(RETRY_LOGIN))
            if retry > 0:
                push(
                    version=version,
                    project_root=project_root,
                    description=description,
                    retry=retry-1,
                )


def main():
    version, project_root, description = sys.argv[1:]

    push(
        version,
        project_root,
        description,
        retry=int(RETRY_PUSH)
    )


if __name__ == "__main__":
    main()
