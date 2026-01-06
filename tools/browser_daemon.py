#!/usr/bin/env python3
"""Browser daemon for fingerprint extraction and traffic capture.

Requires: pip install playwright aiohttp (optional)
Setup: playwright install chromium
"""

import asyncio
import hashlib
import json
import signal
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    print('❌ Playwright not installed')
    print('Run: pip install playwright && playwright install chromium')
    sys.exit(1)


@dataclass
class BrowserFingerprint:
    """Browser fingerprint snapshot."""
    timestamp: str
    user_agent: str
    platform: str
    language: str
    screen: dict
    timezone: str
    hardware_concurrency: int
    device_memory: Optional[int]
    canvas_hash: str
    webgl_vendor: Optional[str]
    webgl_renderer: Optional[str]
    cookies_count: int


class BrowserDaemon:
    """Persistent browser daemon."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.pidfile = Path('artifacts/browser-daemon.pid')
        self.fp_file = Path('artifacts/browser-fingerprint.json')
        self.running = False
    
    async def extract_fingerprint(self) -> BrowserFingerprint:
        """Extract fingerprint from page."""
        js_fp = await self.page.evaluate("""
        () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 200;
            canvas.height = 50;
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Browser FP', 2, 15);
            
            let webgl = null;
            try {
                const gl = document.createElement('canvas').getContext('webgl');
                if (gl) {
                    webgl = {
                        vendor: gl.getParameter(gl.VENDOR),
                        renderer: gl.getParameter(gl.RENDERER)
                    };
                }
            } catch(e) {}
            
            return {
                userAgent: navigator.userAgent,
                platform: navigator.platform,
                language: navigator.language,
                screen: {
                    width: screen.width,
                    height: screen.height,
                    colorDepth: screen.colorDepth
                },
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                canvasData: canvas.toDataURL(),
                webgl: webgl
            };
        }
        """)
        
        canvas_hash = hashlib.md5(js_fp['canvasData'].encode()).hexdigest()[:16]
        cookies = await self.context.cookies()
        
        return BrowserFingerprint(
            timestamp=datetime.now().isoformat(),
            user_agent=js_fp['userAgent'],
            platform=js_fp['platform'],
            language=js_fp['language'],
            screen=js_fp['screen'],
            timezone=js_fp['timezone'],
            hardware_concurrency=js_fp['hardwareConcurrency'],
            device_memory=js_fp.get('deviceMemory'),
            canvas_hash=canvas_hash,
            webgl_vendor=js_fp.get('webgl', {}).get('vendor'),
            webgl_renderer=js_fp.get('webgl', {}).get('renderer'),
            cookies_count=len(cookies)
        )
    
    async def start(self):
        """Start daemon."""
        if self.pidfile.exists():
            print('⚠️  Daemon already running')
            return
        
        self.pidfile.parent.mkdir(parents=True, exist_ok=True)
        
        print('🚀 Starting browser daemon...')
        
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=['--remote-debugging-port=9222']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = await self.context.new_page()
        await self.page.goto('https://www.perplexity.ai')
        
        # Extract fingerprint
        print('🎭 Extracting fingerprint...')
        fp = await self.extract_fingerprint()
        
        self.fp_file.write_text(json.dumps(asdict(fp), indent=2))
        
        print(f'✅ Saved: {self.fp_file}')
        print(f'   Canvas: {fp.canvas_hash}')
        print(f'   UA: {fp.user_agent[:60]}...')
        print(f'   Cookies: {fp.cookies_count}')
        print('')
        print('💡 Use fingerprint in curl_client:')
        print('   python tools/perplexity_curl_client.py "test"')
        print('')
        print('ℹ️  Press Ctrl+C to stop')
        
        import os
        self.pidfile.write_text(str(os.getpid()))
        self.running = True
        
        try:
            while self.running:
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop daemon."""
        print('\n💾 Stopping...')
        
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        
        if self.pidfile.exists():
            self.pidfile.unlink()
        
        print('✅ Stopped')
        self.running = False


async def main():
    if len(sys.argv) < 2:
        print('Usage: browser_daemon.py {start|stop|status}')
        sys.exit(1)
    
    daemon = BrowserDaemon()
    command = sys.argv[1].lower()
    
    if command == 'start':
        def signal_handler(signum, frame):
            daemon.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        await daemon.start()
    
    elif command == 'stop':
        if daemon.pidfile.exists():
            import os
            pid = int(daemon.pidfile.read_text())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f'🛑 Sent SIGTERM to PID {pid}')
            except ProcessLookupError:
                print('❌ Process not found')
                daemon.pidfile.unlink()
        else:
            print('❌ Daemon not running')
    
    elif command == 'status':
        if daemon.pidfile.exists():
            pid = int(daemon.pidfile.read_text())
            print(f'✅ Daemon running (PID: {pid})')
            
            if daemon.fp_file.exists():
                fp = json.loads(daemon.fp_file.read_text())
                print(f'\n🎭 Fingerprint:')
                print(f'   Canvas: {fp["canvas_hash"]}')
                print(f'   Cookies: {fp["cookies_count"]}')
                print(f'   Updated: {fp["timestamp"]}')
        else:
            print('❌ Daemon not running')
    
    else:
        print(f'❌ Unknown: {command}')
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
