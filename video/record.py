import json, time
from playwright.sync_api import sync_playwright
D = json.load(open("durs.json")); GAP = 0.3; LIVE = "https://location-text-parser.vercel.app"
BOX = """(t)=>{let best=null;for(const e of document.body.querySelectorAll('*')){const r=e.getBoundingClientRect();if(r.width&&e.innerText&&e.innerText.includes(t)&&(!best||r.width*r.height<best[1]))best=[e,r.width*r.height]}if(!best)return false;const e=best[0];e.style.background='#ffe36e';e.style.boxShadow='0 0 0 6px #ffe36e';e.style.borderRadius='4px';e.style.color='#1d2a1f';new MutationObserver(()=>{}).observe(e,{attributes:true});return true}"""
HL = """(t)=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const i=n.nodeValue.indexOf(t);if(i>=0){const r=document.createRange();r.setStart(n,i);r.setEnd(n,i+t.length);const m=document.createElement('mark');m.style.cssText='background:#ffe36e;padding:2px 3px;border-radius:4px;box-shadow:0 0 0 3px #ffe36e';r.surroundContents(m);m.scrollIntoView({block:'center'});return true}}return false}"""
OV = """(h)=>{let d=document.getElementById('ov');if(!d){d=document.createElement('div');d.id='ov';document.body.append(d)}d.style.cssText='position:fixed;left:50%;top:40px;transform:translateX(-50%);z-index:99999;background:#1d2a1f;color:#fff;font:600 26px system-ui;padding:18px 30px;border-radius:14px;box-shadow:0 8px 30px #0005;text-align:center;line-height:1.5';d.innerHTML=h}"""
ev = []
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 720}, record_video_dir="rec", record_video_size={"width": 1280, "height": 720})
    pg = ctx.new_page(); T0 = time.monotonic()
    now = lambda: time.monotonic() - T0
    def mark(i):
        # line i may start only after line i-1 finished
        if ev: 
            ready = ev[-1] + D[len(ev) - 1] + GAP
            while now() < ready: time.sleep(0.02)
        ev.append(round(now(), 2))
    def wait_free():
        ready = ev[-1] + D[len(ev) - 1] + GAP
        while now() < ready - 0.05: time.sleep(0.02)
    pg.goto("https://matcha.fm/apply/fse", wait_until="networkidle"); pg.wait_for_timeout(1500); pg.evaluate("document.body.style.zoom='1.45'")
    pg.evaluate("window.scrollTo(0,0)"); pg.get_by_text("Fully remote (US, Canada, Europe, UK, Brazil, LATAM)").locator("visible=true").first.evaluate("e=>{e.style.background='#ffe36e';e.style.boxShadow='0 0 0 6px #ffe36e';e.style.borderRadius='4px';e.style.color='#1d2a1f'}"); pg.wait_for_timeout(300)
    mark(0)
    wait_free(); pg.goto("https://news.ycombinator.com/item?id=50056667", wait_until="networkidle"); pg.evaluate("document.body.style.zoom='1.35'")
    pg.evaluate(HL, "Fully remote anywhere in the world"); mark(1)
    wait_free(); pg.evaluate(OV, "Can someone in India apply?<br><span style='color:#f3a08f'>Job page: no</span> &nbsp;&nbsp; <span style='color:#9fd8ad'>Founder's post: yes</span>"); mark(2)
    wait_free(); pg.goto(LIVE, wait_until="networkidle"); pg.wait_for_selector("#p-searchatlas"); pg.wait_for_timeout(200); mark(3)
    wait_free(); pg.click("#go"); pg.wait_for_timeout(200); mark(4)
    wait_free(); pg.evaluate("()=>{const b=document.getElementById('banner');b.style.boxShadow='0 0 0 5px #e9b4a8';b.style.transition='all .4s';b.style.fontSize='20px';document.querySelector('.india').style.boxShadow='0 0 0 4px #e8c27a'}"); mark(5)
    wait_free(); pg.evaluate("window.scrollTo(0,0)"); pg.click("#p-searchatlas"); pg.wait_for_timeout(250); pg.click("#go"); mark(6)
    wait_free(); pg.evaluate("window.scrollTo(0,0)"); pg.click("#p-prairielearn"); pg.wait_for_timeout(250); pg.click("#go"); mark(7)
    wait_free(); pg.evaluate("document.getElementById('res').scrollIntoView({block:'center'})"); pg.evaluate("document.body.style.zoom='1.0'"); mark(8)
    wait_free(); pg.evaluate("()=>{const r=document.querySelectorAll('#res tr')[2];r.style.background='#ffe36e';r.style.fontWeight='700'}"); mark(9)
    wait_free(); pg.evaluate("()=>{const r=document.querySelectorAll('#res tr')[4];r.style.background='#fbe9e5';r.style.fontWeight='700'}"); mark(10)
    wait_free(); pg.evaluate(OV, "github.com/sivaratrisrinivas/location-text-parser<br><span style='font-weight:400;font-size:22px'>Live: location-text-parser.vercel.app</span>"); pg.evaluate("()=>{const o=document.getElementById('ov');o.style.top='45%'}"); mark(11)
    end = ev[-1] + D[-1] + 1.0
    while now() < end: time.sleep(0.05)
    total = round(now(), 2); vp = pg.video.path(); ctx.close(); b.close()
json.dump({"events": ev, "total": total, "video": vp}, open("timeline.json", "w")); print(ev, total, vp)
