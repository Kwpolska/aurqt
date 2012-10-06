=================
The aurqt project
=================

This is the aurqt project by Kwpolska.  Its goal is to create an “AUR manager”,
i.e. <https://aur.archlinux.org/>, but friendlier, more readable, on the
desktop, and offering an ability to (un)install a package from within the app.

Currently, it’s a work in progress in an early state.  The first thing I want
to begin with is a library to access the AURweb.  Then, I will code an UI in
Qt.  There are designs ready for that in Qt Designer (and they will NOT be used
in the actual thing, so some things are not done right).

But I would love to see some help.  Here are the basic guidelines:

* Use the AURweb interface only if you must.  Otherwise, go with the RPC.
* …and if you are using the RPC, PKGBUILDer.  Specifically, the Utils class.
* Code standards: PEP8, comments, docstrings, everything must be pretty.
* If you want to contribute, throw a pull request or two and ask for
  contributor rights.

Hint, hint: pyuic4.

IMPORTANT NOTE: The AUR will get a 2.0 release soon.  I plan not to bother with
doing stuff with the webui for a while.  A redesign is going to happen, AFAIK.

And now, time for the Kw’s Standard Project 2-Character-Or-Maybe-More
abbreviation (not the logo)::

|                                         ____
|                                  /\    / __ \
|                                 /  \  | |  | |
|                                / /\ \ | |  | |
|                               / ____ \| |__| |
|                              /_/    \_\\___\_\
