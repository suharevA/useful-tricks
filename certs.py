import os
import idna
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def read_certificate_from_file(file_path):
    with open(file_path, "rb") as cert_file:
        pem_data = cert_file.read()
    return pem_data

def load_certificate_from_pem(pem_data):
    certificate = x509.load_pem_x509_certificate(pem_data, backend=default_backend())
    return certificate

def can_wildcard_cert_protect_domain(cert_path, domain):
    pem_data = read_certificate_from_file(cert_path)
    certificate = load_certificate_from_pem(pem_data)
    try:
        subject_alt_names = certificate.extensions.get_extension_for_oid(
            x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        ).value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return False

    # No need to decode the domain here; just use it directly
    for san in subject_alt_names:
        # Directly compare without decoding
        if san == domain:
            return True

    for san in subject_alt_names:
        if san.startswith('*.'):
            # Decode the part of the SAN after the '*' without specifying an encoding
            wildcard_domain = idna.decode(san[2:]).lower()  # Correctly decode only the non-wildcard part
            if domain.endswith(wildcard_domain):
                return True

    return False

def find_suitable_certificate_for_domain(certs_dir, domain):
    for filename in os.listdir(certs_dir):
        if filename.endswith('.crt'):
            cert_path = os.path.join(certs_dir, filename)
            if can_wildcard_cert_protect_domain(cert_path, domain):
                return cert_path
    return None

certs_dir = 'files'
domain_to_check = 'test.test.mos.ru'

suitable_cert = find_suitable_certificate_for_domain(certs_dir, domain_to_check)
if suitable_cert:
    print(f"Found a certificate that can protect {domain_to_check}: {suitable_cert}")
else:
    print(f"No certificate found that can protect {domain_to_check}.")

