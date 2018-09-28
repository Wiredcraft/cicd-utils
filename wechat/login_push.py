import base64
import os
import re
import requests
import subprocess


SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_CHANNELS = os.environ.get("SLACK_CHANNELS", "")
CMD_CLI = "/Applications/wechatwebdevtools.app/Contents/Resources/app.nw/bin/cli"


def decode_image(base64_text, output_file):
    img_data = base64.b64decode(re.sub('^data:image/.+;base64,', '', base64_text))
    with open(output_file, "wb") as file:
        file.write(img_data)


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def login(retry):
    for line in execute([
        CMD_CLI,
        "-l",
        "--login-qr-output base64"]
    ):
        if line.startswith("data:image/jpeg;base64"):
            decode_image(line, "qr.jpg")
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
            login(retry=3)
            if retry > 0:
                push(
                    version=version,
                    project_root=project_root,
                    description=description,
                    retry=retry-1,
                )


def main():
    push("v0.0.1", "/Users/sloppysun/Desktop/test", "Description aaa", retry=3)


if __name__ == "__main__":
    main()
