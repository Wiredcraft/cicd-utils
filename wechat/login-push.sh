#!/bin/bash
###############
# Simple login / push to wechat miniprogram
###############
#
# Note:
#  This version is targetted toward an execution on MacOSX 
#
###############
# ChangeLog
#  20180511 VV Initial creation 
#  20180521 VV Revamp 
###############
#
# Usage:
#   bash login-push.sh /data/my_project v1.0.0 this_is_the_version_description
#
###############

CLI=/Applications/wechatwebdevtools.app/Contents/Resources/app.nw/bin/cli
QR_CODE=$(mktemp)

# Comma separated list of channels to broadcast to
SLACK_CHANNELS=my-channel
SLACK_BOT_TOKEN=my-bot-token

# We expect the config file to include the "real" token & channels
CONFIG_FILE=$(dirname $0)/$(basename $0).conf
if [ -e "$CONFIG_FILE" ]; then
  source $CONFIG_FILE
fi

PROJECT_ROOT="$1"
VERSION="$2"
# The remaining string is the description of the release
shift; shift
DESC="$@"

# TODO clean param cehck (getopts)
if [ -z "${PROJECT_ROOT}" -o -z "${VERSION}" -o -z "${DESC}" ]; then
  echo "Usage: ${basename $0} path version description"  >&2
  echo "   path:         path to the code root"     >&2
  echo "   version:      string"                    >&2
  echo "   description:  multi words allowed"       >&2
  exit 1
fi


##############
# Initialize the CLI / IDE
##############
${CLI} 2>&1 > /dev/null
if [ $? -ne 0 ]; then
  echo "Failure to Initialize the IDE" >&2
  exit 1
fi

# Try to login...
login() {
  for i in $(seq 1 10); do
    # removing legacy login QR
    rm -f ${QR_CODE} ${QR_CODE}.jpg

    ${CLI} -l --login-qr-output base64@${QR_CODE}  2>&1 &
    # ${CLI} -l --login-qr-output base64@${QR_CODE} > /dev/null 2>&1 &
    LOGIN_PID=$!
  
    sleep 5
    if [ -f "${QR_CODE}" ]; then
      # The QR code tend to be failing often - we ensure it's good by checking its size
      size=$(stat -f %z ${QR_CODE})
      if [ ${size} -le 50000 ]; then 
        kill ${LOGIN_PID} 2> /dev/null
        sleep 2
        echo "Too small QR Code - trying again" >&2 
        continue
      fi
      cat ${QR_CODE} | sed -e 's/data:image\/jpeg;base64,//g' | base64 -D > ${QR_CODE}.jpg
      echo -n "Sending QR code to Slack #: ${SLACK_CHANNELS} - "
      curl --silent -F file=@${QR_CODE}.jpg  \
          -F token=${SLACK_BOT_TOKEN} \
          -F channels=${SLACK_CHANNELS} \
          https://slack.com/api/files.upload > /dev/null
      if [ $? -eq 0 ]; then
        echo "[OK]"
      else
        echo "[Error]..."
        exit 1
      fi

      # Wait for completion of the login process...
      while [ 1 ]; do
        ps aux | grep -v grep | grep " ${LOGIN_PID} "
        exist=$(ps aux | grep -v grep | grep -c " ${LOGIN_PID} ")
        if [ $((exist)) -gt 0 ]; then
          sleep 1
          echo -n '.'
        else
          echo "[OK]"
          break
        fi
      done

      # Exit loop and resume attempt at pushing the code 
      break
    else
      kill ${LOGIN_PID} 2> /dev/null
      sleep 2
      echo "Missing QR Code - trying again" >&2 
    fi
  done

  # TODO: Need return status
  return
}

# We're gonna loop up to 10 times - attempting to upload the code base
for i in $(seq 1 10); do
  ${CLI} --upload ${VERSION}@${PROJECT_ROOT} --upload-desc "'${DESC}'" > /dev/null 2>&1 
  if [ $? -eq 0 ]; then
    echo "Upload complete. Exiting"
    exit 
  fi

  # Upload failed - probably because of login...
  # TODO: clean check
  login
done

