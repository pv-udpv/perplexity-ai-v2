#!/usr/bin/env python3
"""Perplexity curl_cffi Client - Standalone CLI tool.

Direct implementation using curl_cffi for production use.
Can be used independently or as validation for library implementation.
"""

import json
import sys
import uuid
from pathlib import Path

# Try library import first
try:
    from perplexity_ai.session import PerplexitySession
    from perplexity_ai.parsers.sse import SSEParser
    USE_LIBRARY = True
except ImportError:
    USE_LIBRARY = False
    from curl_cffi import requests


class PerplexityCurlClient:
    """Standalone curl_cffi client."""
    
    def __init__(
        self,
        fingerprint_file: str = 'artifacts/browser-fingerprint.json',
        cookies_file: str = 'artifacts/browser-cookies.json'
    ):
        if USE_LIBRARY:
            # Use library implementation
            self.session = PerplexitySession()
            self.parser = SSEParser()
        else:
            # Fallback standalone
            self.fp_file = Path(fingerprint_file)
            self.cookies_file = Path(cookies_file)
            
            self.fp = self._load_fingerprint()
            self.cookies = self._load_cookies()
            self.session = self._create_session()
    
    def _load_fingerprint(self) -> dict:
        if not self.fp_file.exists():
            raise FileNotFoundError(f'Fingerprint not found: {self.fp_file}')
        return json.loads(self.fp_file.read_text())
    
    def _load_cookies(self) -> dict:
        if not self.cookies_file.exists():
            return {}
        
        cookies_data = json.loads(self.cookies_file.read_text())
        cookies = {}
        for cookie in cookies_data:
            if 'perplexity.ai' in cookie.get('domain', ''):
                cookies[cookie['name']] = cookie['value']
        
        return cookies
    
    def _create_session(self):
        import re
        ua = self.fp['user_agent']
        chrome_match = re.search(r'Chrome/(\d+)', ua)
        chrome_version = int(chrome_match.group(1)) if chrome_match else 120
        
        if chrome_version >= 120:
            impersonate = "chrome120"
        elif chrome_version >= 110:
            impersonate = "chrome110"
        else:
            impersonate = "chrome101"
        
        platform_map = {
            'Win32': 'Windows',
            'Windows': 'Windows',
            'MacIntel': 'macOS',
            'Linux x86_64': 'Linux',
        }
        platform_name = platform_map.get(self.fp['platform'], 'Unknown')
        
        headers = {
            'User-Agent': ua,
            'Accept': 'text/event-stream',
            'Accept-Language': f"{self.fp['language']},en;q=0.9",
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Sec-Ch-Ua': f'"Not;A=Brand";v="24", "Chromium";v="{chrome_version}"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': f'"{platform_name}"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Origin': 'https://www.perplexity.ai',
            'Referer': 'https://www.perplexity.ai/',
        }
        
        return requests.Session(
            headers=headers,
            cookies=self.cookies,
            impersonate=impersonate
        )
    
    def _build_payload(self, query: str, mode: str = 'concise') -> dict:
        return {
            'query_str': query,
            'version': '2.18',
            'source': 'default',
            'language': self.fp.get('language', 'en-US') if not USE_LIBRARY else 'en-US',
            'timezone': self.fp.get('timezone', 'America/New_York') if not USE_LIBRARY else 'America/New_York',
            'mode': mode,
            'attachments': [],
            'sources': ['web'],
            'search_recency_filter': None,
            'search_focus': 'internet',
            'frontend_uuid': str(uuid.uuid4()),
            'frontend_context_uuid': str(uuid.uuid4()),
            'model_preference': 'pplx-pro' if mode == 'copilot' else 'turbo',
            'is_related_query': False,
            'is_sponsored': False,
            'prompt_source': 'user',
            'query_source': 'user',
            'is_incognito': False,
            'local_search_enabled': False,
            'use_schematized_api': True,
            'send_back_text_in_streaming_api': False,
            'supported_block_use_cases': [
                'answer_modes', 'media_items', 'knowledge_cards',
                'inline_entity_cards', 'place_widgets'
            ],
            'client_coordinates': {
                'location_lat': 40.7128,
                'location_lng': -74.006
            },
            'mentions': [],
            'skip_search_enabled': True,
            'is_nav_suggestions_disabled': False,
            'always_search_override': False,
            'override_no_search': False,
            'should_ask_for_mcptool_confirmation': True,
            'browser_agent_allow_once_from_toggle': False,
            'force_enable_browser_agent': False,
            'supported_features': ['browser_agent_permission_banner.v1.1']
        }
    
    def _parse_response_fallback(self, text: str) -> dict:
        """Fallback parser if library not available."""
        steps = []
        
        for line in text.split('\n'):
            if not line.startswith('data: '):
                continue
            
            try:
                data = json.loads(line[6:])
                if isinstance(data, list):
                    steps.extend(data)
                elif isinstance(data, dict):
                    steps.append(data)
            except json.JSONDecodeError:
                pass
        
        for step in steps:
            if step.get('step_type') == 'FINAL':
                content = step.get('content', {})
                answer_str = content.get('answer', '')
                
                if answer_str:
                    try:
                        answer_obj = json.loads(answer_str)
                        return {
                            'text': answer_obj.get('answer', ''),
                            'web_results': answer_obj.get('web_results', []),
                            'structured_answer': answer_obj.get('structured_answer'),
                        }
                    except json.JSONDecodeError:
                        return {'text': answer_str, 'web_results': [], 'structured_answer': None}
        
        return {'text': '', 'web_results': [], 'structured_answer': None}
    
    def ask(self, query: str, mode: str = 'concise', raw: bool = False) -> str | dict:
        """Ask question."""
        payload = self._build_payload(query, mode)
        
        response = self.session.post(
            'https://www.perplexity.ai/rest/sse/perplexity_ask',
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f'HTTP {response.status_code}: {response.text[:200]}')
        
        if USE_LIBRARY:
            events = self.parser.parse_complete(response.text)
            result = self.parser.extract_answer(events)
        else:
            result = self._parse_response_fallback(response.text)
        
        return result if raw else result['text']


def main():
    if len(sys.argv) < 2:
        print('Perplexity curl_cffi Client')
        print('')
        print('Usage:')
        print('  python tools/perplexity_curl_client.py "Question"')
        print('  python tools/perplexity_curl_client.py --pro "Question"')
        print('  python tools/perplexity_curl_client.py --raw "Question"')
        print('')
        print(f'Library mode: {"ENABLED" if USE_LIBRARY else "DISABLED (fallback)"}')
        sys.exit(1)
    
    try:
        client = PerplexityCurlClient()
    except FileNotFoundError as e:
        print(f'❌ {e}')
        print('Run: python tools/browser_daemon.py start')
        sys.exit(1)
    
    mode = 'concise'
    raw = False
    args_idx = 1
    
    while args_idx < len(sys.argv) and sys.argv[args_idx].startswith('--'):
        if sys.argv[args_idx] == '--pro':
            mode = 'copilot'
        elif sys.argv[args_idx] == '--raw':
            raw = True
        args_idx += 1
    
    query = ' '.join(sys.argv[args_idx:])
    
    if not query:
        print('❌ No question provided')
        sys.exit(1)
    
    print(f'🔍 {query}')
    print(f'⚙️  Mode: {mode}')
    print('⏳ Waiting...\n')
    
    try:
        result = client.ask(query, mode=mode, raw=raw)
        
        if raw:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f'📝 {result}')
    except Exception as e:
        print(f'❌ {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
