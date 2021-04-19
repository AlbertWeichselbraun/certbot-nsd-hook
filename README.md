# Provides a hook for updating nsd zones with certbot DNS authentification (required for wildcard domains)

## Dependencies

- python-dnspython

## Setup

### cerbot

Install the certbot-nsd-hook script and then call certbot as follows:

```bash
cerbot certonly \
       -d '*.yourdomain.com'  \
       --manual  \
       --manual-auth-hook="/opt/certbot-nsd-hook/nsd-update-dns.py" \
       --post-hook="systemctl reload apache2"
``` 
- `-d` ... the domain for which you require the certificate
- `--manual-auth-hook` ... location of the `nsd-update-dns.py` script
- `--post-hook` ... command used for reloading your web server

The script asumes that the nsd config file is available at `/etc/nsd/nsd.conf`. 


### NSD zone file 

- must contain a valid DNS and SOA record (required by python-dnspython)
- should contain a TXT record that is then used for updating the acme challenge
  ```
  _acme-challenge 60 IN TXT "dummy"
  ``` 

