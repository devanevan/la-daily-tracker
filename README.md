# LA Daily Tracker

Small script which tracks your dailies via OCR, saving the amount of endgame gold earning raids you left per character to a redis hashset.

Supply the redis url via a .env with the key: REDIS_URL

Currently, (x,y) and width/height are based on 21:9 1440p monitor.