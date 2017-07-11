#!/bin/bash

http post \
    https://getpocket.com/v3/get \
    consumer_key=$POCKET_CONSUMER_KEY \
    access_token=$POCKET_ACCESS_TOKEN \
    state=archive \
    detailType=simple \
    > ~/tmp/pocket-archive-`date +%Y%m%d%H%M`.json
