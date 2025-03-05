from urllib.parse import urlparse


def get_domain(url):
    """Extract domain"""
    if url and url.strip():
        data = urlparse(url)
        return data.hostname

    return ""
