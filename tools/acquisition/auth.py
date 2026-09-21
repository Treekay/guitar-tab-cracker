"""Local opt-in browser session configuration and secret-free diagnostics."""
import os

BROWSERS = ('edge', 'chrome', 'firefox')
SESSION_ERRORS = {'authentication_required', 'session_required', 'access_restricted'}
COOKIE_ERRORS = {'cookies_unavailable', 'browser_profile_locked', 'browser_not_installed'}

MESSAGES = {
    'authentication_required': 'Verify that you can access this video while logged into your browser, or provide a local video file.',
    'session_required': 'The site requires session context. Use an authorized browser session or provide a local video file.',
    'cookies_unavailable': 'Browser cookies could not be read or decrypted for this site. Verify your browser session or provide a local video file.',
    'browser_profile_locked': 'Browser cookie database is locked or inaccessible. Close the selected browser and retry, or provide a local video file.',
    'browser_not_installed': 'The selected browser profile/cookie database was not found. Select an installed browser or provide a local video file.',
    'rate_limited': 'The site rate-limited this request. Try later or provide a local video file.',
    'unsupported_url': 'This URL or media format is not supported by the acquisition backend. Provide a local video file.',
    'network_error': 'The connection or metadata request failed or timed out. Try later or provide a local video file.',
    'download_failed': 'The downloader could not acquire the video. Provide a local video file.',
    'drm_or_protected': 'Protected content is not supported. No protection bypass was attempted.',
    'access_restricted': 'The site denied this request. Use only a session already authorized to access the video, or provide a local file.',
    'invalid_media': 'The downloaded file is not valid video. Provide a local video file.',
    'ffmpeg_validation_failed': 'The downloaded media failed ffprobe/ffmpeg validation. Provide a local video file.',
}

def message(reason):
    return MESSAGES.get(reason, MESSAGES['download_failed'])

def browser_sources(explicit=None, automatic=False):
    if explicit and automatic:
        raise ValueError('Choose explicit browser mode or automatic fallback, not both')
    sources = [explicit] if explicit else (os.environ.get('GTC_BROWSER_COOKIE_SOURCES', 'edge,chrome,firefox').split(',') if automatic else [])
    sources = list(dict.fromkeys(x.strip().lower() for x in sources))
    if any(x not in BROWSERS for x in sources):
        raise ValueError('Cookie sources must be browser names: edge, chrome, firefox; arbitrary profile paths are not accepted')
    return sources

def add_arguments(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--cookies-from-browser', choices=BROWSERS)
    group.add_argument('--auto-browser-cookies', action='store_true')

def classify(message_text):
    text = message_text.lower()
    if any(x in text for x in ('drm', 'protected content', 'paywall')): return 'drm_or_protected'
    if any(x in text for x in ('429', 'too many requests', 'rate limit')): return 'rate_limited'
    if any(x in text for x in ('database is locked', 'could not copy', 'permission denied', 'winerror 32')): return 'browser_profile_locked'
    if 'could not find' in text and any(x in text for x in ('cookie', 'profile', 'browser')): return 'browser_not_installed'
    if any(x in text for x in ('decrypt', 'dpapi', 'failed to load cookies', 'cookies unavailable')): return 'cookies_unavailable'
    if any(x in text for x in ('sign in', 'login', 'log in', 'logged-in', 'authentication', 'private video', 'members-only', 'premium', 'http error 401')): return 'authentication_required'
    if any(x in text for x in ('http error 412', 'captcha', 'session required', 'cookies required', 'access challenge')): return 'session_required'
    if 'http error 403' in text: return 'access_restricted'
    if any(x in text for x in ('timed out', 'timeout', 'connection', 'dns', 'name resolution', 'network', 'certificate')): return 'network_error'
    if any(x in text for x in ('unsupported url', 'no suitable', 'no video formats', 'not a valid url')): return 'unsupported_url'
    return 'download_failed'

def exception_reason(error):
    # Examine chains in memory only; never persist potentially secret messages.
    from acquisition.security import AcquisitionError
    seen = set()
    while error and id(error) not in seen:
        seen.add(id(error))
        if isinstance(error, AcquisitionError): return error.reason
        reason = classify(str(error))
        child = error.__cause__ or error.__context__
        if child and reason in ('download_failed', 'cookies_unavailable'):
            error = child
            continue
        return reason
    return 'download_failed'
