It is helpful to run the urwid UI under GNU screen, but that has trouble with 256 colors.

to get it working:

1) Compile `screen` from source
```
$ git clone https://git.savannah.gnu.org/git/screen.git
```

2) compile with flag - needs libpam(something)-dev

```
$ ./autogen.sh
$ ./configure --enable-colors256
```

3) set env variable
```
export TERM=xterm-256color
```
