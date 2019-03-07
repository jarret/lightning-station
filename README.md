Junk
====
Apologies for a sparse README. This is a work-in-progress and is a bit of an artisan project that lacks professional polish at the moment. Thanks for looking at the source code, though.

This is the `bitcoind` and `c-lightining` node monitor panel and jukebox invoicing.

`run_py.sh` and `run_dev.sh` are the scripts which invoke the main script. The first is the 'production' environment on the Raspberry Pi. The second is my 'development' environment on my linux laptop. Both have parameters that connect to the nodes where I have them.

For the Lightning Network Bolt11 QR code, the `--webserver` option in `run_dev.sh` serves a html file at port 80 and a websocket connection for something that kind of looks like a e-ink display, but seen in a web browser. In `run_py.sh`, it will instead initialize the Waveshare e-ink display on the Pi's GPIO as well as the input buttons.

The music audio files refrenced by the JSON in `jukebox.py` are not hosted/provided in this repo. The actual `.mp3` files will need to be made available in a directory and provided in the launch script.

If the code exceptions, it is hard to see with the `urwid` interface on the terminal and in the way. You can instead run with the `--console` option when launching and it will just print text instead of the console. Makes it much easier to see an exception if it occurs.



That's all the docs I will write now. For everything else, you will need to reed the code or come out to the Edmonton Bitcoin Meetup's Bitcoin Hack Day for a better explanation.

License
====

This code is licensed under the MIT License as defined in LICENSE. Have Fun!

The e-ink display stuff under `waveshare/` is also MIT. The source is copied from my `raspi-uart-waveshare` repo, which is documented better.
