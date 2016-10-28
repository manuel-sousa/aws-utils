# aws-utils
Collection of scripts to simplify AWS Operations

## updateRoute53.py
Script to make changes to all records of one domain from command line.
  
##### Usage
```
./updateRoute53.py -h
usage: updateRoute53.py [-h] [--dryrun] [--waitForSync]
                        [--maximumFetchItems N] [--SOA] [--NS] [-v] [-d]
                        {ttl,replaceIp} ...

Change Route53 domain records

optional arguments:
  -h, --help            show this help message and exit
  --dryrun              don't submit record change
  --waitForSync         wait for changes to propagate
  --maximumFetchItems N
                        maximum items to fetch (default: 100)
  --SOA                 change SOA record
  --NS                  change NS record
  -v, --verbose         verbose
  -d, --debug           debug

subcommands:
  available commands

  {ttl,replaceIp}       additional help
    ttl                 change domain records TTL
    replaceIp           change server ip for all records
```

### Functions
#### ttl
Changes the ttl of all records in a domain
##### Usage
```
./updateRoute53.py ttl -h
usage: updateRoute53.py ttl [-h] --domain DOMAIN [--ttl TTL]

optional arguments:
  -h, --help       show this help message and exit
  --domain DOMAIN  domain to change
  --ttl TTL        ttl to set (default: 14440)
```
#### replaceIp
Replaces all references of one IP to a new one
##### Usage
```
usage: updateRoute53.py replaceIp [-h] --domain DOMAIN --oldIP OLDIP --newIP
                                  NEWIP

optional arguments:
  -h, --help       show this help message and exit
  --domain DOMAIN  domain to change
  --oldIP OLDIP    old ip address
  --newIP NEWIP    new ip address
```
