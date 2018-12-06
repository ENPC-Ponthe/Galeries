# JWT auth keys directory

Necessary for the mobile API authentication. Generate them with :
```
openssl genrsa -out jwtRS256-private.pem 2048 && openssl rsa -in jwtRS256-private.pem -pubout -out jwtRS256-public.pem
```