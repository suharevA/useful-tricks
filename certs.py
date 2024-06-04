from cryptography import x509
from cryptography.hazmat.backends import default_backend
import os
import idna  # Import the idna library for Punycode decoding

def read_certificate_from_file(file_path):
    """
    Reads an X.509 certificate from a file.

    :param file_path: Path to the certificate file.
    :return: Certificate data in bytes.
    """
    with open(file_path, "rb") as cert_file:
        pem_data = cert_file.read()
    return pem_data

def load_certificate_from_pem(pem_data):
    """
    Loads an X.509 certificate from PEM data.

    :param pem_data: Certificate data in PEM format.
    :return: Certificate object.
    """
    certificate = x509.load_pem_x509_certificate(
        pem_data,
        backend=default_backend()
    )
    return certificate

def can_wildcard_cert_protect_domain(cert_path, domain):
    """
    Checks if a wildcard certificate can protect a specified domain, including handling Punycode-encoded domains.

    :param cert_path: Path to the certificate file.
    :param domain: Domain to check.
    :return: True if the certificate can protect the domain, False otherwise.
    """
    # Read the certificate from the file
    pem_data = read_certificate_from_file(cert_path)
    certificate = load_certificate_from_pem(pem_data)

    # Extract subject alternative names
    try:
        subject_alt_names = certificate.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        ).value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return False

    # Decode the domain to its Unicode form if it's encoded in Punycode
    decoded_domain = idna.decode(domain).lower()

    # Check if the domain matches any of the patterns in the subject alternative names
    for san in subject_alt_names:
        if san.startswith('*.'):
            # Remove the wildcard part and compare the rest of the domain
            wildcard_domain = san[2:].lower()
            # Decode the wildcard domain to its Unicode form if it's encoded in Punycode
            decoded_wildcard_domain = idna.decode(wildcard_domain).lower()
            if decoded_domain.endswith(decoded_wildcard_domain):
                return True
    return False

# Directory containing the.crt files
certs_dir = 'files'
# Domain to check
domain_to_check = 'test.zakupki.mos.ru'  # Example domain in Punycode

# Function to find a suitable certificate for a domain
def find_suitable_certificate_for_domain(certs_dir, domain):
    for filename in os.listdir(certs_dir):
        if filename.endswith('.crt'):
            cert_path = os.path.join(certs_dir, filename)
            if can_wildcard_cert_protect_domain(cert_path, domain):
                return cert_path
    return None

# Find and print the suitable certificate for the given domain
suitable_cert = find_suitable_certificate_for_domain(certs_dir, domain_to_check)
if suitable_cert:
    print(f"Найден сертификат, который может защитить {domain_to_check}: {suitable_cert}")
else:
    print(f"Не найден сертификат, который может защитить {domain_to_check}.")
