#!/bin/bash
docker compose down
sleep 2
$(screen -X -S log quit ; cd /root/django-telegram-bot/ ; screen -dmS log docker compose up --build)
screen -x log