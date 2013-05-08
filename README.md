# RAX Dynamic DNS
## Synopsis

This script can be used as a pseudo-dynamic DNS client with Rackspace Cloud DNS.  It can be run on hosts whether they are on the Rackspace Cloud or not, however it does require that the zone file for the domain be hosted on the Rackspace Cloud DNS.  The script will obtain your host's public IP address, and update it's A record within the DNS.  As long as the DNS record has a short TTL, it will update quickly.

## Installation

Tested on Python 2.7.1.  Requires the '[pyrax](https://github.com/rackspace/pyrax)' Python module in addition to various standard modules that are included with Python.  The required configuration file ([detailed below](#config)) should be installed as `.raxdyndns` in the user's root of their home directory.

## Usage

    usage: rax-dyndns.py [-h] [-q] [-V]
    
    Obtain your workstation IP Address, and update it's DNS entry in the
    Rackspace Cloud DNS
    
    optional arguments:
      -h, --help     show this help message and exit
      -q             Silence output
      -V, --version  show program's version number and exit

## <a name="config"></a>Sample Configuration File (.raxdyndns)

    [raxdyndns]
    dyn_hostname: macbook
    zone: mydomain.com
    
    [rackspace_cloud]
    username: user1234
    api_key: 1234567890abcdefghijkl

## License

   Copyright 2013 Javier Ayala

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

   [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.