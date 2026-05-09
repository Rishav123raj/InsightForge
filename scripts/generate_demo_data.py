from __future__ import annotations
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "backend" / "data" / "csv"
PDF = ROOT / "backend" / "data" / "pdfs"
random.seed(42)

MOVIES = [
    ("m1", "Stellar Run", "Sci-Fi", "2025-02-14", 90000000, "Orion"),
    ("m2", "Dark Orbit", "Sci-Fi", "2025-04-18", 110000000, "Orion"),
    ("m3", "Last Kingdom", "Drama", "2025-03-07", 70000000, "Northstar"),
    ("m4", "Laugh Track", "Comedy", "2025-06-20", 35000000, "Sunny"),
    ("m5", "City Beats", "Musical", "2025-08-01", 45000000, "Pulse"),
    ("m6", "Midnight Chef", "Comedy", "2025-10-10", 25000000, "Sunny"),
    ("m7", "Rogue Signal", "Action", "2025-09-12", 85000000, "Northstar"),
]
CITIES = ["New York", "Los Angeles", "Chicago", "Austin", "Seattle", "Miami"]
SEGMENTS = ["18-24", "25-34", "35-44", "45-54"]

def write_csv(name, rows):
    CSV.mkdir(parents=True, exist_ok=True)
    with (CSV / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def simple_pdf(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [title, ""] + [body[i:i+86] for i in range(0, len(body), 86)]
    commands = ["BT /F1 12 Tf 50 760 Td"]
    for idx, line in enumerate(lines[:42]):
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if idx: commands.append("0 -16 Td")
        commands.append(f"({safe}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode()
    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream)} >> stream\n".encode()+stream+b"\nendstream endobj\n",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(out)); out.extend(obj)
    xref = len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for off in offsets[1:]: out.extend(f"{off:010d} 00000 n \n".encode())
    out.extend(f"trailer << /Root 1 0 R /Size {len(objects)+1} >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(out)

def main():
    write_csv("movies.csv", [dict(movie_id=a,title=b,genre=c,release_date=d,budget=e,studio=f) for a,b,c,d,e,f in MOVIES])
    viewers=[]
    for i in range(1,151): viewers.append(dict(viewer_id=f"v{i}",age_segment=random.choice(SEGMENTS),city=random.choice(CITIES),country="US",subscription_tier=random.choice(["Basic","Plus","Premium"]),email=f"viewer{i}@example.internal"))
    write_csv("viewers.csv", viewers)
    acts=[]; reviews=[]; start=date(2025,1,1)
    for i in range(1,1401):
        movie=random.choice(MOVIES); viewer=random.choice(viewers); d=start+timedelta(days=random.randrange(365))
        boost=1.45 if movie[1] in ["Stellar Run","Dark Orbit"] else .75 if movie[2]=="Comedy" else 1
        minutes=round(random.uniform(20,130)*boost,1)
        acts.append(dict(activity_id=f"a{i}",viewer_id=viewer['viewer_id'],movie_id=movie[0],watch_date=d.isoformat(),minutes_watched=minutes,completed=1 if minutes>85 else 0,device=random.choice(["TV","Mobile","Web"])))
        if i % 3 == 0:
            base=4.5 if movie[1]=="Stellar Run" else 4.1 if movie[1]=="Dark Orbit" else 2.8 if movie[2]=="Comedy" else 3.8
            rating=max(1,min(5,round(random.gauss(base,.55),1)))
            reviews.append(dict(review_id=f"r{i}",viewer_id=viewer['viewer_id'],movie_id=movie[0],review_date=d.isoformat(),rating=rating,sentiment="positive" if rating>=4 else "negative" if rating<3 else "neutral",comment="Demo internal review summary"))
    write_csv("watch_activity.csv", acts); write_csv("reviews.csv", reviews)
    spend=[]; regions=[]; sid=1; rid=1
    for movie in MOVIES:
        for month in range(1,13):
            for channel in ["Search","Social","Streaming Promo"]:
                amt=random.randint(20000,120000)*(1.4 if movie[1]=="Stellar Run" else .65 if movie[2]=="Comedy" else 1)
                spend.append(dict(spend_id=f"s{sid}",movie_id=movie[0],campaign=f"{movie[1]} Launch",channel=channel,spend_date=f"2025-{month:02d}-15",amount=round(amt,2),impressions=int(amt*random.uniform(18,35)),clicks=int(amt*random.uniform(.8,2.2)))); sid+=1
            for city in CITIES:
                trend=month/12
                mult=1.9 if movie[1]=="Stellar Run" and month>=9 else 1.4 if movie[1]=="Dark Orbit" else .62 if movie[2]=="Comedy" else 1
                city_mult=1.35 if city=="New York" else 1.15 if city=="Los Angeles" else 1
                views=int(random.randint(1200,6200)*mult*city_mult*(.7+trend))
                regions.append(dict(row_id=f"rp{rid}",movie_id=movie[0],city=city,month=f"2025-{month:02d}",views=views,completion_rate=round(random.uniform(.48,.88)*(.8 if movie[2]=="Comedy" else 1),3),revenue=round(views*random.uniform(2.4,4.8),2))); rid+=1
    write_csv("marketing_spend.csv", spend); write_csv("regional_performance.csv", regions)
    docs = {
        "quarterly_executive_report.pdf": "Stellar Run became the flagship growth title in Q4 2025 due to repeat viewing, strong 25-34 engagement, and New York over-performance. Leadership should fund sci-fi retention bundles and premium-tier experiments.",
        "campaign_performance_summary.pdf": "Dark Orbit delivered efficient paid search conversion, while comedy campaigns suffered from creative fatigue, weak trailer completion, and rising social acquisition costs. Stellar Run trended after influencer clips and soundtrack memes.",
        "content_roadmap.pdf": "The 2026 roadmap prioritizes sci-fi franchises, action sequels, city-based launch events, and a comedy format reset with shorter pilots before wide release.",
        "policy_guidelines.pdf": "Internal analytics assistants must use approved tools, least-privilege role scopes, masked PII, audit traces, and summarized evidence rather than exposing raw viewer records.",
        "audience_behavior_report.pdf": "Premium subscribers aged 25-34 showed the strongest engagement with sci-fi and action titles. New York and Los Angeles led completion rates in late 2025.",
    }
    for name, body in docs.items(): simple_pdf(PDF/name, name.replace('_',' ').replace('.pdf','').title(), body)
if __name__ == "__main__": main()