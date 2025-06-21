#!/usr/bin/env sh

ssh-add "$(find ~/Sync/ssh/ -type f ! -name '*.pub')"
ssh-add "$(find ~/Documents/_int/ssh-keys/ -type f ! -name '*.pub')"

exit 0
