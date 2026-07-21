#!/usr/bin/env python3

import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "demo_result.json"

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ChainLens</title>
<style>
body{
    margin:0;
    background:#07111b;
    color:#edf6ff;
    font-family:Arial,sans-serif
}
.container{
    max-width:1200px;
    margin:auto;
    padding:25px
}
header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:25px
}
h1{
    margin:0;
    font-size:40px
}
.subtitle{
    color:#91a7b9;
    margin-top:6px
}
.badge{
    display:inline-block;
    padding:8px 12px;
    border:1px solid #29445b;
    border-radius:20px;
    margin-left:5px;
    font-size:12px
}
.safe{color:#59e391}
.paper{color:#ffd166}
.grid{
    display:grid;
    grid-template-columns:2fr 1fr;
    gap:18px
}
.panel{
    background:#0d1c29;
    border:1px solid #233b4f;
    border-radius:16px;
    padding:20px
}
.metrics{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:12px
}
.metric{
    background:#102231;
    padding:15px;
    border-radius:12px
}
.label{
    color:#91a7b9;
    font-size:12px
}
.value{
    font-size:25px;
    font-weight:bold;
    margin-top:6px
}
.regime{
    margin-top:18px;
    padding:20px;
    border:1px solid #2c536d;
    border-radius:14px
}
#regime{
    font-size:30px;
    font-weight:bold;
    margin:8px 0
}
#decision{
    color:#5de4ff;
    font-size:18px;
    font-weight:bold
}
.row{
    display:grid;
    grid-template-columns:150px 1fr 55px;
    gap:10px;
    align-items:center;
    margin:16px 0
}
.track{
    height:10px;
    background:#07111b;
    border-radius:10px;
    overflow:hidden
}
.bar{
    height:100%;
    transition:width .5s
}
.pin{background:#ffd166}
.conf{background:#5de4ff}
.bear{background:#ff6b6b}
.bull{background:#59e391}
.levels{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:10px;
    margin-top:20px
}
.level{
    background:#102231;
    padding:14px;
    border-radius:12px
}
.explain{
    margin-top:20px;
    padding-top:18px;
    border-top:1px solid #233b4f;
    line-height:1.6
}
.step{
    padding:13px;
    margin:8px 0;
    background:#102231;
    border:1px solid #233b4f;
    border-radius:10px;
    cursor:pointer
}
.step.active{
    border-color:#5de4ff
}
button{
    padding:10px 14px;
    margin:5px;
    background:#153149;
    border:1px solid #31546e;
    color:white;
    border-radius:8px;
    cursor:pointer
}
.warning{
    margin-top:20px;
    color:#ffd166;
    font-size:13px
}
@media(max-width:800px){
    .grid{grid-template-columns:1fr}
    .metrics{grid-template-columns:1fr}
}
</style>
</head>

<body>
<div class="container">

<header>
<div>
<h1>ChainLens</h1>
<div class="subtitle">Explainable Options Decision Auditor</div>
</div>

<div>
<span class="badge paper">VERIFIED HISTORICAL REPLAY</span>
<span class="badge safe">PAPER ONLY</span>
<span class="badge safe">REAL ORDERS DISABLED</span>
</div>
</header>

<div class="grid">

<div>
<div class="metrics">
<div class="metric">
<div class="label">REPLAY TIME</div>
<div class="value" id="time">N/A</div>
</div>

<div class="metric">
<div class="label">NIFTY SPOT</div>
<div class="value" id="spot">N/A</div>
</div>

<div class="metric">
<div class="label">INDIA VIX</div>
<div class="value" id="vix">N/A</div>
</div>
</div>

<div class="panel" style="margin-top:18px">

<div class="regime">
<div class="label">MARKET STRUCTURE</div>
<div id="regime">N/A</div>
<div id="signal">N/A</div>
<br>
<div id="decision">N/A</div>
</div>

<div class="row">
<div>Pin Risk</div>
<div class="track"><div id="pinbar" class="bar pin"></div></div>
<div id="pin">N/A</div>
</div>

<div class="row">
<div>Confidence</div>
<div class="track"><div id="confbar" class="bar conf"></div></div>
<div id="confidence">N/A</div>
</div>

<div class="row">
<div>Bearish Pressure</div>
<div class="track"><div id="bearbar" class="bar bear"></div></div>
<div id="bear">N/A</div>
</div>

<div class="row">
<div>Bullish Pressure</div>
<div class="track"><div id="bullbar" class="bar bull"></div></div>
<div id="bull">N/A</div>
</div>

<div class="levels">
<div class="level">
<div class="label">SUPPORT / GATE</div>
<div class="value" id="support">N/A</div>
</div>

<div class="level">
<div class="label">RESISTANCE</div>
<div class="value" id="resistance">N/A</div>
</div>

<div class="level">
<div class="label">TARGET</div>
<div class="value" id="target">N/A</div>
</div>
</div>

<div class="explain">
<div class="label">WHY CHAINLENS SAYS THIS</div>
<p id="explanation">N/A</p>
</div>

</div>
</div>

<div class="panel">
<h3>Decision Timeline</h3>
<div id="timeline"></div>

<button onclick="previous()">Previous</button>
<button onclick="next()">Next</button>
<button id="auto" onclick="autoPlay()">Auto Play</button>

<div class="warning">
Research and paper-trading demonstration only.<br>
No real-money order execution.
</div>
</div>

</div>
</div>

<script>
let data;
let index=0;
let timer=null;

function id(x){return document.getElementById(x)}

function display(value, suffix=""){
    return (value===null||value===undefined||value==="") ? "N/A" : value+suffix;
}

function bar(name,value){
    const width=(typeof value==="number"&&Number.isFinite(value))
        ? Math.min(100,Math.max(0,value))
        : 0;
    id(name).style.width=width+"%"
}

function render(){
    const x=data.timeline[index];

    id("time").innerText=display(x.time);
    id("spot").innerText=display(x.spot);
    id("vix").innerText=display(x.vix);

    id("regime").innerText=display(x.regime);
    id("signal").innerText=display(x.signal);
    id("decision").innerText=display(x.decision);

    id("pin").innerText=display(x.pin_risk,"%");
    id("confidence").innerText=display(x.confidence,"%");
    id("bear").innerText=display(x.bearish_pressure,"%");
    id("bull").innerText=display(x.bullish_pressure,"%");

    bar("pinbar",x.pin_risk);
    bar("confbar",x.confidence);
    bar("bearbar",x.bearish_pressure);
    bar("bullbar",x.bullish_pressure);

    id("support").innerText=display(x.support);
    id("resistance").innerText=display(x.resistance);
    id("target").innerText=display(x.target);

    id("explanation").innerText=display(x.explanation);

    document.querySelectorAll(".step").forEach((e,i)=>{
        e.classList.toggle("active",i===index);
    });
}

function buildTimeline(){
    id("timeline").innerHTML=data.timeline.map((x,i)=>
        `<div class="step" onclick="index=${i};render()">
        <b>${x.time}</b><br>
        ${x.signal}<br>
        <span style="color:#91a7b9;font-size:12px">${x.regime}</span>
        </div>`
    ).join("");
}

function next(){
    if(index<data.timeline.length-1){
        index++;
        render();
    }
}

function previous(){
    if(index>0){
        index--;
        render();
    }
}

function autoPlay(){
    if(timer){
        clearInterval(timer);
        timer=null;
        id("auto").innerText="Auto Play";
        return;
    }

    index=0;
    render();
    id("auto").innerText="Stop";

    timer=setInterval(()=>{
        if(index>=data.timeline.length-1){
            clearInterval(timer);
            timer=null;
            id("auto").innerText="Auto Play";
            return;
        }
        index++;
        render();
    },2500);
}

fetch("/api/state")
.then(r=>{
    if(!r.ok) throw new Error(`Replay request failed: ${r.status}`);
    return r.json();
})
.then(x=>{
    if(!Array.isArray(x.timeline)||x.timeline.length===0){
        throw new Error("Replay timeline is empty or invalid");
    }
    data=x;
    buildTimeline();
    render();
})
.catch(error=>{
    id("timeline").innerText="Replay unavailable";
    console.error(error);
});
</script>

</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):

    def send_data(self, body, content_type):
        body = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/":
            self.send_data(HTML, "text/html; charset=utf-8")
            return

        if self.path == "/api/state":
            payload = DATA.read_text(encoding="utf-8")
            self.send_data(payload, "application/json; charset=utf-8")
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":

    if not DATA.exists():
        raise SystemExit("demo_result.json missing")

    data = json.loads(DATA.read_text(encoding="utf-8"))

    if data.get("real_orders_allowed") is not False:
        raise SystemExit(
            "SAFETY FAILURE: real_orders_allowed must be false"
        )

    if data.get("paper_only") is not True:
        raise SystemExit(
            "SAFETY FAILURE: paper_only must be true"
        )

    HOST="0.0.0.0"
    PORT=8898

    print("="*60)
    print("CHAINLENS BUILD WEEK DEMO")
    print("MODE: VERIFIED HISTORICAL REPLAY")
    print("PAPER ONLY: YES")
    print("REAL ORDERS: DISABLED")
    print(f"PORT: {PORT}")
    print("="*60)

    ThreadingHTTPServer(
        (HOST,PORT),
        Handler
    ).serve_forever()
