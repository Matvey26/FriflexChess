import os
import certifi

def setup_environment():
    os.environ['SSL_CERT_FILE'] = certifi.where()

def create_output_dir(base_dir="tts_outputs"):
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_dir)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir