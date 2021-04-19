# Provides a hook for updating nsd zones with certbot DNS authentification (required for wildcard domains)

## Dependencies

- python-dnspython

## Zone file 

- must contain a valid DNS and SOA record (required by python-dnspython)
- should contain a TXT record that is used for updating the acme challenge
  ```
  _acme-challenge 60 IN TXT "dummy"
  ``` 

