# TLS Certificates for MQTT Security

This directory contains the TLS/SSL certificates required for secure MQTT communication in the ConsultEase system. Follow these instructions to generate the necessary certificates.

## Required Certificate Files

- `ca.crt`: Certificate Authority certificate
- `client.crt`: Client certificate
- `client.key`: Client private key

## Certificate Generation Instructions

### Prerequisites

1. Install OpenSSL
   - Ubuntu/Debian: `sudo apt install openssl`
   - Windows: Download from [OpenSSL's website](https://www.openssl.org/source/) or use Git Bash
   - macOS: Already installed or use Homebrew: `brew install openssl`

### Step 1: Create a Certificate Authority (CA)

```bash
# Create private key for CA
openssl genrsa -out ca.key 2048

# Create CA certificate
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=ConsultEase CA"
```

### Step 2: Create Client Certificate

```bash
# Create client key
openssl genrsa -out client.key 2048

# Create certificate signing request
openssl req -new -key client.key -out client.csr -subj "/CN=ConsultEase Client"

# Sign the client certificate with our CA
openssl x509 -req -days 3650 -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt
```

### Step 3: Configure MQTT Broker

#### For Mosquitto Broker

Add these lines to your `/etc/mosquitto/mosquitto.conf`:

```
# TLS/SSL Configuration
listener 8883
cafile /path/to/ca.crt
certfile /path/to/server.crt
keyfile /path/to/server.key

# Client authentication
require_certificate true
use_identity_as_username true
```

### Step 4: Update ConsultEase Config

Ensure the following settings are in your `config.env`:

```
TLS_ENABLED=True
TLS_CA_CERT=certs/ca.crt
TLS_CLIENT_CERT=certs/client.crt
TLS_CLIENT_KEY=certs/client.key
TLS_INSECURE=False
```

## Security Recommendations

1. Keep private keys (`.key` files) secure
2. Never share private keys
3. Set secure permissions: `chmod 400 *.key`
4. Consider using a hardware security module (HSM) for production
5. Rotate certificates annually

## Testing TLS Connection

To test your MQTT TLS connection:

```bash
# Subscribe to a topic with TLS
mosquitto_sub -h your-broker.com -p 8883 \
  --cafile certs/ca.crt \
  --cert certs/client.crt \
  --key certs/client.key \
  -t "test/topic" -v

# Publish to a topic with TLS
mosquitto_pub -h your-broker.com -p 8883 \
  --cafile certs/ca.crt \
  --cert certs/client.crt \
  --key certs/client.key \
  -t "test/topic" -m "TLS test message"
``` 