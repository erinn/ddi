[![image](https://travis-ci.org/erinn/ddi.svg?branch=master)](https://travis-ci.org/erinn/ddi)
[![codecov](https://codecov.io/gh/erinn/ddi/branch/master/graph/badge.svg)](https://codecov.io/gh/erinn/ddi)

# DDI
DDI is a simple client to allow quick interaction with the SolidServer IPAM. 
Other backends should be possible but at the moment only SolidServer is supported.

## Installation:
In the future this program should be available as an RPM from RHEL >= 8 and
current Fedora releases.

This program forgoes using setuptools for [flit](https://pypi.org/project/flit/) so
flit must first be installed in order to install ddi. 

To install flit and ddi local to your user, in the ddi base directory run: 

    pip install --user flit
    flit install --user 

### Development Installation:
To install ddi in a development environment 
[pipenv](https://pypi.org/project/pipenv/) must first be installed. After pipenv
is installed setup the environment and then run flit to symlink in the library
like so:

    pipenv install --dev
    pipenv shell
    flit install --symlink 
    
After that is done you will have a vitrualenv with the required packages installed
and the ddi entrypoint will by symlinked with the code allowing you to develop
and run against your development code.

## Usage:
Make sure, at a minimum, you read the sections on setting your username, 
setting your password, and setting the server address.

### Environment Variables:
**ALL** options and arguments within ddi can be passed in as environment variables. 
The basic syntax of this is PROGRAMENAME_OPTION or PROGRAMENAME_ARG. This will be more
easily illustrated by examples:

    ddi --help
    Usage: ddi [OPTIONS] COMMAND [ARGS]...
    
    Options:
      -D, --debug          Enable debug output.  [default: False]
      -S, --secure         TLS verification.  [default: True]
      -J, --json           Output in JSON.  [default: False]
      -P, --password TEXT  The DDI user's password.
      -s, --server TEXT    The DDI server's URL to connect to.  [required]
      -U, --username TEXT  The DDI username.  [default: <USERNAME>; required]
      --version            Show the version and exit.
      --help               Show this message and exit.
    
    Commands:
      host      Host based commands.
      password  Password commands


So to set the debug option as an environment variable you would (in bash):

    export DDI_DEBUG=true

Or to set the server:

    export DDI_SERVER=https://ddi.example.com

For arguments passed in you can use environment variables as well if you wish, 
for example:

    $ddi host info --help
    Usage: ddi host info [OPTIONS] [HOSTS]...
    
      Provide the DDI info on the given host(s).
    
    Options:
      --help  Show this message and exit.
      
To pass in the HOSTS arguments and an env variable you would do the following:

    export DDI_HOST_INFO_HOSTS=host1.example.com host2.example.com

Finally for nested commands like 'ddi host add':

    ddi host add --help
    Usage: ddi host add [OPTIONS] HOST
    
      Add a single host entry into DDI
    
    Options:
      -b, --building TEXT    The UCB building the host is in.  [required]
      --comment TEXT         Additional comment for the host.
      -c, --contact TEXT     The UCB contact for the host.  [required]
      -d, --department TEXT  The UCB department the host belongs to.  [required]
      -i, --ip TEXT          The IPv4 address for the host.  [required]
      -p, --phone TEXT       The UCB phone number associated with the host.
                             [required]
      --help                 Show this message and exit.

To set the building you would do the following:

    export DDI_HOST_ADD_BUILDING=BAR

You should get the idea. This behaviour is global.

### Set Your Username:
If the username you have set on your system is not the same as the username to
be used with DDI either pass the '-U/--username' flag after every 'ddi' command:
i.e: 
    
    ddi -U foo host info example.com

Or set the DDI_USERNAME environment variable in your shell.

### Set Your Password:
Because the SolidServer IPAM only supports username and password authentication
your password must be stored somewhere. There are three options available for 
password storage, in order from most to least secure:
1. Keyring
2. Environment Variable
3. Command line parameter

#### Keyring:
Keyring utilizes the systems secure storage, on OSX this is keychain, on Windows
Credential Locker, on Linux Kwallet and the like. This is probably your most secure
option for credential storage. In order to use it, run the following:

    ddi password set

You will be prompted for your password and it will then be stored in the systems
secure credential storage.

#### Environment Variable:
You can pass your password in by setting the **DDI_PASSWORD** environment variable
in your shell.

#### Command Line Parameter:
Finally and least secure, you can pass your password in on the command line like
so:

    ddi -P my_insecure_password host delete example.com
    
### Set Your Server:
Much the same as setting the username or password the full URL to the server
must be set for every command either via the command line -s/--server flag or via
the **DDI_SERVER** environment variable. If the server is not set you will be 
prompted to enter the server's URL.

Environment variable example:

    export DDI_SERVER=https://ddi.example.com
    
Command line example:

    ddi -s https://ddi.example.com host delete bar.example.com

## RPM Release Procedure
1. Bump __version__ in ddi/__init__.py
2. run flit build
3. Copy or link dist/ddi-\<version\>.tar.gz to rpmbuild/sources
4. Bump the changelog in ddi.spec 
5. Copy or link ddi.spec to rpmbuild/specs
6. in rpmbuild/ run rpmbuild -bs specs/ddi.spec
7. Use you favorite tool like mock to build the rpm on the platform.
