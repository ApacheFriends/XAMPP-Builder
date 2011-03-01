XAMPP Builder
=============

XAMPP Builder will be replace the current bash-based build system used for XAMPP for Mac OS X. It'll be modular and allow to declare depentencies in order to not forget rebuilding something.

The Builder is written in Python and is designed to be adopted by the other *nix systems XAMPP is avaiable for.

Design
------------

    utils/ -- will contain the utils and all the classes used by this builder
    components/ -- will contain the components for XAMPP along with their dependencies and configure/build descriptions
    builder.py -- will be the script that is interacted with and used to build XAMPP
    default.ini -- will be the default config used for the paths where the zips, the builds etc. should be stored

Let's hope everything works as I imagine.
