# Certs

Certs for validation of the PostgreSQL server connection with sslmod=verify-full

See <https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-networking-ssl-tls#configure-ssl-on-the-client>

## Making the bundle

From the above page, there are links to 3 root CA certificates:

- <https://www.microsoft.com/pkiops/certs/Microsoft%20RSA%20Root%20Certificate%20Authority%202017.crt>
- <https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem>
- <https://cacerts.digicert.com/DigiCertGlobalRootCA.crt>

Download each of these, and convert the two `.crt` files to `.pem` format with `openssl`:

```bash
openssl x509 -inform DER -in Microsoft_RSA_Root_CA_2017.crt -out Microsoft_RSA_Root_CA_2017.crt.pem -outform PEM
```

```bash
openssl x509 -inform DER -in DigiCertGlobalRootCA.crt -out DigiCertGlobalRootCA.pem -outform PEM
```

Then combine all the `.pem` files into a single bundle:

```bash
cat Microsoft_RSA_Root_CA_2017.crt.pem DigiCertGlobalRootG2.crt.pem DigiCertGlobalRootCA.crt.pem > azure_postgres_ca_bundle.pem
```
