#!/usr/bin/env sh

# shellcheck disable=SC2046
ssh-add $(find ~/Sync/ssh/ -type f ! -name '*.pub')
ssh-add $(find ~/Documents/_int/ssh-keys/ -type f ! -name '*.pub')

exit 0
