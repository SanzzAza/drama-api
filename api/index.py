#!/usr/bin/env python3
# api/index.py - DramaCina Multi Platform for Vercel

import requests as req
import json
import re
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# ============================================================
# KONFIGURASI
# ============================================================

GS_BASE  = "https://captain.sapimu.au/goodshort"
DB_BASE  = "https://captain.sapimu.au/dramaboxv4"
ML_BASE  = "https://melolo.dramabos.my.id"
DBT_BASE = "https://captain.sapimu.au/dramabite"
DNV_BASE = "https://captain.sapimu.au/dramanova"

TOKEN_MAIN = "5a6df8230521283fad1e9d4590b619171793e8173953af434e478929c761b2ed"
TOKEN_ML   = "04AA0FC87491A42A11A33C32610CD172"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept"    : "application/json, text/plain, */*",
    "Origin"    : "https://dramacina.vip",
    "Referer"   : "https://dramacina.vip/",
}

AUTH_H = {
    "token": TOKEN_MAIN,
    "Authorization": f"Bearer {TOKEN_MAIN}",
    "Content-Type": "application/json"
}

ML_H = {
    "token": TOKEN_ML,
    "Authorization": f"Bearer {TOKEN_ML}",
    "Content-Type": "application/json",
    "Origin": "https://melolo.dramabos.my.id",
    "Referer": "https://melolo.dramabos.my.id/",
    "Accept": "application/json, text/plain, */*",
}

GS_CHANNELS = {"id": 562, "pt": 564, "kr": 565, "th": 568}

s = req.Session()
s.headers.update(HEADERS)

# ============================================================
# HELPERS
# ============================================================

def clean(t):
    return re.sub(r"<[^>]+>", "", str(t)).strip() if t else ""

def ok(action, source, result):
    return {"creator": "SanzzXD", "status": True, "code": 200, "action": action, "source": source, "result": result}

def err(action, source, msg):
    return {"creator": "SanzzXD", "status": False, "code": 400, "action": action, "source": source, "message": msg}

def dx(url, params=None, hdrs=None):
    try:
        h = {**HEADERS, **(hdrs or {})}
        r = s.get(url, params=params, headers=h, timeout=20)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def p(key, default=""):
    return request.args.get(key, default)

def pi(key, default=1):
    try:
        return int(request.args.get(key, default))
    except:
        return default

# ============================================================
# GOODSHORT
# ============================================================

def gs_home(page=1, channel="id"):
    channel_id = GS_CHANNELS.get(channel, 562)
    r = dx(f"{GS_BASE}/api/v1/home", {"channelId": channel_id, "page": page, "pageSize": 12, "language": "id"}, AUTH_H)
    if not r: return err("home", "goodshort", "gagal")
    data = r.get("data", {}) or {}
    records = data.get("records", []) or []
    sections, flat_items, seen = [], [], set()
    for rec in records:
        sec = {"channelId": rec.get("channelId", 0), "columnId": rec.get("columnId", 0), "name": rec.get("name", ""), "style": rec.get("style", ""), "more": rec.get("more", False), "items": []}
        for x in (rec.get("items", []) or []):
            bid = str(x.get("bookId") or x.get("action") or "")
            title = x.get("bookName") or x.get("name", "")
            cover = x.get("cover") or x.get("image", "")
            if not bid: continue
            item = {"id": bid, "title": title, "cover": cover, "image": x.get("image") or x.get("cover", ""), "introduction": clean(x.get("introduction", "")), "labels": x.get("labels", []) or [], "labelInfos": x.get("labelInfos", []) or [], "viewCount": x.get("viewCount", 0), "viewCountDisplay": x.get("viewCountDisplay", ""), "chapterCount": x.get("chapterCount", 0), "firstChapterId": x.get("firstChapterId", 0), "bookType": x.get("bookType", 0), "grade": x.get("grade", ""), "ratings": x.get("ratings", 0), "typeTwoNames": x.get("typeTwoNames", []) or [], "member": x.get("member", 0), "columnStyle": x.get("columnStyle", ""), "fullHDEnable": x.get("fullHDEnable", False), "downloadEnable": x.get("downloadEnable", False), "platform": "goodshort"}
            if x.get("scheduledReleaseDay"): item["scheduledReleaseDay"] = x["scheduledReleaseDay"]
            if x.get("scheduledReleaseDayOfTime"): item["scheduledReleaseDayOfTime"] = x["scheduledReleaseDayOfTime"]
            sec["items"].append(item)
            if bid not in seen and title: seen.add(bid); flat_items.append(item)
        sections.append(sec)
    return ok("home", "goodshort", {"page": data.get("current", page), "pageSize": data.get("size", 12), "totalSections": data.get("total", len(records)), "channelId": channel_id, "channel": channel, "sections": sections, "items": flat_items, "totalItems": len(flat_items)})

def gs_search(kw, page=1):
    r = dx(f"{GS_BASE}/api/v1/search", {"q": kw, "language": "id", "page": page, "pageSize": 20}, AUTH_H)
    if not r: return err("search", "goodshort", "gagal")
    sr = r.get("data", {}).get("searchResult", {})
    items = sr.get("records", []) if isinstance(sr, dict) else []
    dramas = [{"id": str(x.get("bookId", "")), "title": x.get("bookName") or x.get("name", ""), "cover": x.get("cover", ""), "introduction": clean(x.get("introduction", "")), "labels": x.get("labels", []) or [], "viewCount": x.get("viewCount", 0), "viewCountDisplay": x.get("viewCountDisplay", ""), "chapterCount": x.get("chapterCount", 0), "firstChapterId": x.get("firstChapterId", 0), "grade": x.get("grade", ""), "typeTwoNames": x.get("typeTwoNames", []) or [], "platform": "goodshort"} for x in items]
    return ok("search", "goodshort", {"keyword": kw, "items": dramas, "total": len(dramas)})

def gs_detail(bid):
    r = dx(f"{GS_BASE}/api/v1/book/{bid}", {"language": "id"}, AUTH_H)
    if not r: return err("detail", "goodshort", "gagal")
    data = r.get("data", {}) or {}; book = data.get("book", {}) or {}; lst = data.get("list", []) or []
    episodes = []
    for i, ch in enumerate(lst):
        chapter_id = str(ch.get("id", ""))
        ql = []
        for mv in (ch.get("multiVideos", []) or []):
            cdn = mv.get("cdnList", []) or []; q_url = cdn[0].get("videoPath", "") if cdn else mv.get("filePath", "")
            if q_url: ql.append({"label": mv.get("type", ""), "url": q_url, "type": "hls"})
        cdn_urls = [c.get("videoPath", "") for c in (ch.get("cdnList", []) or []) if c.get("videoPath")]
        episodes.append({"episode": i + 1, "chapterId": chapter_id, "title": ch.get("chapterName", f"Episode {i+1}"), "locked": bool(ch.get("charged", False)), "price": ch.get("price", 0), "free": ch.get("price", 0) == 0, "playTime": ch.get("playTime", 0), "playCount": ch.get("playCount", 0), "playCountDisplay": ch.get("playCountDisplay", ""), "image": ch.get("image", ""), "buyWay": ch.get("buyWay", ""), "payWay": ch.get("payWay", ""), "cdnUrl": ch.get("cdn", ""), "cdnUrls": cdn_urls, "qualities": ql})
    return ok("detail", "goodshort", {"data": {"id": str(book.get("bookId", bid)), "title": book.get("bookName", ""), "cover": book.get("cover", ""), "detailCover": book.get("bookDetailCover", ""), "synopsis": clean(book.get("introduction", "")), "totalEpisodes": book.get("chapterCount", len(episodes)), "viewCount": book.get("viewCount", 0), "viewCountDisplay": book.get("viewCountDisplay", ""), "ratings": book.get("ratings", 0), "commentCount": book.get("commentCount", 0), "followCount": book.get("followCount", 0), "totalWords": book.get("totalWords", 0), "tags": book.get("labels", []), "labelInfos": book.get("labelInfos", []), "status": book.get("writeStatus", ""), "language": book.get("languageDisplay", ""), "unit": book.get("unit", ""), "grade": book.get("grade", ""), "freeEpisodes": book.get("free", 0), "memberEpisodes": book.get("member", 0), "producer": book.get("producer", ""), "playwright": book.get("playwright", ""), "protagonist": book.get("protagonist", ""), "pseudonym": book.get("pseudonym", ""), "fullHDEnable": book.get("fullHDEnable", False), "downloadEnable": book.get("downloadEnable", False), "episodes": episodes, "platform": "goodshort"}})

def gs_key(bid, chapter_id):
    r = dx(f"{GS_BASE}/api/v1/key", {"bookId": bid, "chapterId": chapter_id}, AUTH_H)
    return r.get("key", "") if r else ""

def gs_stream(bid, ep=1, quality="720p"):
    rd = dx(f"{GS_BASE}/api/v1/book/{bid}", {"language": "id"}, AUTH_H)
    if not rd: return err("stream", "goodshort", "gagal ambil detail")
    data = rd.get("data", {}) or {}; book = data.get("book", {}) or {}; lst = data.get("list", []) or []
    if not lst: return err("stream", "goodshort", "tidak ada episode")
    idx = min(ep - 1, len(lst) - 1); ch = lst[idx]; chapter_id = str(ch.get("id", ""))
    if not chapter_id: return err("stream", "goodshort", "chapterId tidak ditemukan")
    rp = dx(f"{GS_BASE}/api/v1/play/{bid}/{chapter_id}", {"q": quality, "language": "id"}, AUTH_H)
    if not rp: return err("stream", "goodshort", "gagal ambil video")
    m3u8 = rp.get("m3u8", ""); aes = gs_key(bid, chapter_id)
    ql = []
    for mv in (ch.get("multiVideos", []) or []):
        cdn = mv.get("cdnList", []) or []; q_url = cdn[0].get("videoPath", "") if cdn else mv.get("filePath", "")
        if q_url: ql.append({"label": mv.get("type", ""), "url": q_url, "type": "hls"})
    if not ql and m3u8: ql.append({"label": quality, "url": m3u8, "type": "hls"})
    return ok("stream", "goodshort", {"bookId": bid, "chapterId": chapter_id, "episode": idx + 1, "totalEps": len(lst), "title": book.get("bookName", ""), "epTitle": ch.get("chapterName", f"Episode {idx+1}"), "videoUrl": m3u8, "quality": quality, "aesKey": aes, "kEncrypted": rp.get("k", ""), "sSeed": rp.get("s", ""), "isLocked": bool(ch.get("charged", False)), "isFree": not bool(ch.get("charged", False)), "qualityList": ql})

def gs_stream_fast(bid, ep=1, quality="720p"):
    r = dx(f"{GS_BASE}/api/v1/unlock/{bid}", {"q": quality}, AUTH_H)
    if not r: return err("stream_fast", "goodshort", "gagal unlock")
    videos = r.get("videos", []) or []; total = r.get("total", len(videos))
    if not videos: return err("stream_fast", "goodshort", "tidak ada episode")
    idx = min(ep - 1, len(videos) - 1); target = videos[idx]; chapter_id = str(target.get("id", "")); url = target.get("url", "")
    aes = gs_key(bid, chapter_id) if chapter_id else ""
    all_eps = [{"episode": i + 1, "chapterId": str(v.get("id", "")), "name": v.get("name", ""), "url": v.get("url", ""), "type": "hls"} for i, v in enumerate(videos)]
    return ok("stream_fast", "goodshort", {"bookId": bid, "chapterId": chapter_id, "episode": idx + 1, "totalEps": total, "videoUrl": url, "quality": quality, "aesKey": aes, "qualityList": [{"label": quality, "url": url, "type": "hls"}] if url else [], "allEpisodes": all_eps})

def gs_unlock_all(bid, quality="720p"):
    r = dx(f"{GS_BASE}/api/v1/unlock/{bid}", {"q": quality}, AUTH_H)
    if not r: return err("unlock", "goodshort", "gagal")
    videos = r.get("videos", []) or []
    episodes = [{"episode": i + 1, "chapterId": str(v.get("id", "")), "name": v.get("name", ""), "url": v.get("url", ""), "type": "hls"} for i, v in enumerate(videos)]
    return ok("unlock", "goodshort", {"bookId": bid, "quality": quality, "total": r.get("total", len(videos)), "episodes": episodes})

# ============================================================
# DRAMABOX
# ============================================================

def db_home(page=1, size=10, lang="in"):
    r = dx(f"{DB_BASE}/api/home", {"page": page, "size": size, "lang": lang}, AUTH_H)
    if not r: return err("home", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {}); sections_raw = root.get("sections", []) or []
    sections, flat_items, seen = [], [], set()
    for sec in sections_raw:
        books = sec.get("books", []) or []; parsed_books = []
        for b in books:
            item = {"id": str(b.get("bookId", "")), "title": b.get("bookName", ""), "cover": b.get("coverWap", ""), "episodes": b.get("chapterCount", 0), "synopsis": clean(b.get("introduction", "")), "tags": b.get("tags", []) or [], "tagV3s": b.get("tagV3s", []) or [], "isEntry": b.get("isEntry", 0), "index": b.get("index", 0), "corner": b.get("corner", {}), "dataFrom": b.get("dataFrom", ""), "cardType": b.get("cardType", 0), "markNamesConnectKey": b.get("markNamesConnectKey", ""), "playCount": b.get("playCount", ""), "bookShelfTime": b.get("bookShelfTime", 0), "shelfTime": b.get("shelfTime", ""), "inLibrary": b.get("inLibrary", False), "platform": "dramabox"}
            parsed_books.append(item)
            if item["id"] and item["id"] not in seen: seen.add(item["id"]); flat_items.append(item)
        sections.append({"id": sec.get("id", 0), "title": sec.get("title", ""), "subTitle": sec.get("subTitle", ""), "style": sec.get("style", ""), "type": sec.get("type", ""), "books": parsed_books})
    return ok("home", "dramabox", {"code": r.get("code", 0), "message": r.get("message", ""), "page": page, "size": size, "lang": lang, "sections": sections, "items": flat_items, "totalSections": len(sections), "totalItems": len(flat_items)})

def db_rank(lang="in"):
    r = dx(f"{DB_BASE}/api/rank", {"lang": lang}, AUTH_H)
    if not r: return err("rank", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {}); rank_types = root.get("rankTypeVoList", []) or []; rank_list = root.get("rankList", []) or []
    items = [{"id": str(x.get("bookId", "")), "title": x.get("bookName", ""), "cover": x.get("coverWap", ""), "episodes": x.get("chapterCount", 0), "synopsis": clean(x.get("introduction", "")), "tags": x.get("tags", []) or [], "tagV3s": x.get("tagV3s", []) or [], "isEntry": x.get("isEntry", 0), "index": x.get("index", 0), "protagonist": x.get("protagonist", ""), "dataFrom": x.get("dataFrom", ""), "cardType": x.get("cardType", 0), "rankVo": x.get("rankVo", {}), "markNamesConnectKey": x.get("markNamesConnectKey", ""), "playCount": x.get("playCount", ""), "bookShelfTime": x.get("bookShelfTime", 0), "shelfTime": x.get("shelfTime", ""), "corner": x.get("corner", {}), "inLibrary": x.get("inLibrary", False), "platform": "dramabox"} for x in rank_list]
    return ok("rank", "dramabox", {"code": r.get("code", 0), "message": r.get("message", ""), "lang": lang, "rankTypes": rank_types, "items": items, "total": len(items)})

def db_search(keyword, page=1, lang="in"):
    r = dx(f"{DB_BASE}/api/search", {"keyword": keyword, "page": page, "lang": lang}, AUTH_H)
    if not r: return err("search", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {}); search_list = root.get("searchList", []) or []
    items = [{"id": str(x.get("bookId", "")), "title": x.get("bookName", ""), "cover": x.get("cover", ""), "synopsis": clean(x.get("introduction", "")), "author": x.get("author", ""), "inLibraryCount": x.get("inLibraryCount", 0), "bookSource": x.get("bookSource", {}), "playCount": x.get("playCount", ""), "sort": x.get("sort", 0), "protagonist": x.get("protagonist", ""), "tagNames": x.get("tagNames", []) or [], "corner": x.get("corner", {}), "markNamesConnectKey": x.get("markNamesConnectKey", ""), "algorithmRecomDot": x.get("algorithmRecomDot", ""), "inLibrary": x.get("inLibrary", False), "platform": "dramabox"} for x in search_list]
    return ok("search", "dramabox", {"code": r.get("code", 0), "message": r.get("message", ""), "keyword": root.get("keyword", keyword), "page": page, "lang": lang, "items": items, "total": len(items)})

def db_detail(did, lang="en"):
    r = dx(f"{DB_BASE}/api/drama/{did}", {"lang": lang}, AUTH_H)
    if not r: return err("detail", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {}); lst = root.get("list", []) or []
    episodes = [{"episode": i + 1, "chapterId": str(ch.get("chapterId", "")), "chapterIndex": ch.get("chapterIndex", i), "isCharge": ch.get("isCharge", 0), "isPay": ch.get("isPay", 0), "chapterSizeVoList": ch.get("chapterSizeVoList", []) or []} for i, ch in enumerate(lst)]
    return ok("detail", "dramabox", {"code": r.get("code", 0), "message": r.get("message", ""), "data": {"id": str(root.get("bookId", did)), "title": root.get("bookName", ""), "cover": root.get("coverWap", "") or root.get("cover", ""), "synopsis": clean(root.get("introduction", "")) or clean(root.get("description", "")), "bookStatus": root.get("bookStatus", 0), "corner": root.get("corner", {}), "crossChapter": root.get("crossChapter", False), "crossChapterTips": root.get("crossChapterTips", ""), "episodes": episodes, "totalEpisodes": len(episodes), "platform": "dramabox"}})

def db_episodes(did, lang="in"):
    r = dx(f"{DB_BASE}/api/drama/{did}/episodes", {"lang": lang}, AUTH_H)
    if not r: return err("episodes", "dramabox", "gagal")
    root = r.get("data", {}); eps = root.get("episodes", []) or []
    episodes = []
    for e in eps:
        qlabel = f'{e.get("quality", "Auto")}p' if isinstance(e.get("quality"), int) else str(e.get("quality", "Auto"))
        ql = [{"label": qlabel, "url": e.get("url", ""), "type": "mp4"}] if e.get("url") else []
        episodes.append({"episode": e.get("episode", 0), "chapterId": str(e.get("chapterId", "")), "chapterName": e.get("chapterName", ""), "cover": e.get("cover", ""), "quality": e.get("quality", 0), "url": e.get("url", ""), "subtitles": e.get("subtitles", []) or [], "qualityList": ql})
    return ok("episodes", "dramabox", {"code": r.get("code", 0), "message": r.get("message", ""), "bookId": root.get("bookId", did), "bookName": root.get("bookName", ""), "cover": root.get("cover", ""), "description": clean(root.get("description", "")), "totalEpisodes": root.get("totalEpisodes", len(episodes)), "quality": root.get("quality", 0), "episodes": episodes, "platform": "dramabox"})

# ============================================================
# MELOLO
# ============================================================

def ml_home(lang="id", offset=0):
    r = dx(f"{ML_BASE}/api/home", {"lang": lang, "offset": offset}, ML_H)
    if not r or r.get("code") != 0: return err("home", "melolo", "gagal")
    items = r.get("data", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("name", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "synopsis": clean(x.get("intro", "")), "platform": "melolo"} for x in items]
    return ok("home", "melolo", {"lang": lang, "offset": offset, "items": dramas, "total": len(dramas)})

def ml_search(kw, lang="id"):
    r = dx(f"{ML_BASE}/api/search", {"q": kw, "lang": lang}, ML_H)
    if not r or r.get("code") != 0: return err("search", "melolo", "gagal")
    items = r.get("data", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("name", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "synopsis": clean(x.get("intro", "")), "author": x.get("author", ""), "platform": "melolo"} for x in items]
    return ok("search", "melolo", {"keyword": kw, "lang": lang, "count": r.get("count", len(dramas)), "items": dramas, "total": len(dramas)})

def ml_detail(did, lang="id"):
    r = dx(f"{ML_BASE}/api/detail/{did}", {"lang": lang}, ML_H)
    if not r or r.get("code") != 0: return err("detail", "melolo", "gagal")
    videos = r.get("videos", []) or []
    ep_list = [{"episode": v.get("episode", 0), "vid": str(v.get("vid", "")), "duration": v.get("duration", 0)} for v in videos]
    return ok("detail", "melolo", {"data": {"id": str(r.get("id", did)), "title": r.get("title", ""), "cover": r.get("cover", ""), "episodes": r.get("episodes", len(ep_list)), "synopsis": clean(r.get("intro", "")), "videos": ep_list, "platform": "melolo"}})

def ml_video(did, ep=1):
    try:
        candidate_ids = [str(did)]
        detail = dx(f"{ML_BASE}/api/detail/{did}", {"lang": "id"}, ML_H)
        if detail and detail.get("code") == 0:
            for v in (detail.get("videos", []) or []):
                if int(v.get("episode", 0)) == int(ep):
                    vid = str(v.get("vid", ""))
                    if vid and vid not in candidate_ids: candidate_ids.append(vid)
                    break
        last_error = "gagal"
        for current_id in candidate_ids:
            h = {**HEADERS, **ML_H}
            r = s.get(f"{ML_BASE}/api/video", params={"id": current_id, "ep": ep, "code": TOKEN_ML}, headers=h, timeout=20)
            if r.status_code != 200: last_error = f"HTTP {r.status_code}"; continue
            try: data = r.json()
            except: last_error = "response bukan json"; continue
            if data.get("code") != 200: last_error = data.get("msg") or data.get("message") or f"code={data.get('code')}"; continue
            ql = data.get("qualityList", []) or []
            quality_list = [{"label": q.get("label", ""), "url": q.get("url", ""), "type": "mp4"} for q in ql]
            return ok("video", "melolo", {"dramaId": did, "usedId": current_id, "episode": data.get("episodeNumber", ep), "number": data.get("number", ep), "videoUrl": data.get("videoUrl", ""), "locked": data.get("locked", False), "qualityList": quality_list, "platform": "melolo"})
        return err("video", "melolo", f"{last_error} | tried={candidate_ids}")
    except Exception as e:
        return err("video", "melolo", str(e))

# ============================================================
# DRAMABITE
# ============================================================

def dbt_dramas(lang="id", page=0):
    r = dx(f"{DBT_BASE}/api/v1/dramas", {"lang": lang, "page": page}, AUTH_H)
    if r is None: return err("dramas", "dramabite", "gagal request")
    items = r if isinstance(r, list) else []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "platform": "dramabite"} for x in items if isinstance(x, dict)]
    return ok("dramas", "dramabite", {"lang": lang, "page": page, "items": dramas, "total": len(dramas), "hasMore": len(dramas) > 0})

def dbt_foryou(lang="id", page=0):
    r = dx(f"{DBT_BASE}/api/v1/foryou", {"lang": lang, "page": page}, AUTH_H)
    if r is None: return err("foryou", "dramabite", "gagal request")
    items = r if isinstance(r, list) else []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "platform": "dramabite"} for x in items if isinstance(x, dict)]
    return ok("foryou", "dramabite", {"lang": lang, "page": page, "items": dramas, "total": len(dramas), "hasMore": len(dramas) > 0})

def dbt_hot(lang="id"):
    r = dx(f"{DBT_BASE}/api/v1/hot", {"lang": lang}, AUTH_H)
    if r is None: return err("hot", "dramabite", "gagal request")
    items = r if isinstance(r, list) else []
    keywords = [{"keyword": k.get("title", ""), "dramaId": str(k.get("cid", ""))} for k in items if isinstance(k, dict)]
    return ok("hot", "dramabite", {"lang": lang, "keywords": keywords, "total": len(keywords)})

def dbt_recommend(lang="id", page=0):
    r = dx(f"{DBT_BASE}/api/v1/recommend", {"lang": lang, "page": page}, AUTH_H)
    if r is None: return err("recommend", "dramabite", "gagal request")
    items = r if isinstance(r, list) else []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "platform": "dramabite"} for x in items if isinstance(x, dict)]
    return ok("recommend", "dramabite", {"lang": lang, "page": page, "items": dramas, "total": len(dramas)})

def dbt_search(kw, lang="id", limit=20):
    r = dx(f"{DBT_BASE}/api/v1/search", {"q": kw, "lang": lang, "limit": limit}, AUTH_H)
    if r is None: return err("search", "dramabite", "gagal request")
    items = r if isinstance(r, list) else []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "platform": "dramabite"} for x in items if isinstance(x, dict)]
    return ok("search", "dramabite", {"keyword": kw, "lang": lang, "limit": limit, "items": dramas, "total": len(dramas)})

def dbt_detail(did, lang="id"):
    r = dx(f"{DBT_BASE}/api/v1/drama/{did}", {"lang": lang}, AUTH_H)
    if r is None: return err("detail", "dramabite", "gagal request")
    if not isinstance(r, dict): return err("detail", "dramabite", "response bukan dict")
    eps_raw = r.get("episodes", []) or []
    episodes = [{"episode": ep.get("number", ep.get("id", 0)), "id": ep.get("id", 0), "title": ep.get("title", ""), "free": ep.get("free", False), "locked": not ep.get("free", False)} for ep in eps_raw if isinstance(ep, dict)]
    return ok("detail", "dramabite", {"data": {"id": str(r.get("id", did)), "cover": r.get("cover") or "", "totalEpisodes": len(episodes), "episodes": episodes, "platform": "dramabite"}})

def dbt_likes(did, lang="id"):
    r = dx(f"{DBT_BASE}/api/v1/drama/{did}/likes", {"lang": lang}, AUTH_H)
    if r is None: return err("likes", "dramabite", "gagal request")
    if not isinstance(r, dict): return err("likes", "dramabite", "response bukan dict")
    return ok("likes", "dramabite", {"dramaId": str(r.get("cid", did)), "likeCount": r.get("like_num", 0), "shareCount": r.get("share_num", 0), "collectCount": r.get("collected_num", 0), "platform": "dramabite"})

def dbt_episode(did, ep, lang="id", quality="default"):
    r = dx(f"{DBT_BASE}/api/v1/drama/{did}/episode/{ep}", {"lang": lang, "quality": quality}, AUTH_H)
    if r is None: return err("episode", "dramabite", "gagal request")
    if not isinstance(r, dict): return err("episode", "dramabite", "response bukan dict")
    video_url = r.get("video", ""); vid_type = "hls" if ".m3u8" in video_url else "mp4" if ".mp4" in video_url else "hls"
    quality_list = [{"label": quality if quality != "default" else "auto", "url": video_url, "type": vid_type}] if video_url else []
    return ok("episode", "dramabite", {"dramaId": did, "episode": r.get("number", ep), "id": r.get("id", 0), "title": r.get("title", f"Episode {ep}"), "videoUrl": video_url, "quality": quality, "validFor": r.get("validFor", 0), "qualityList": quality_list, "platform": "dramabite"})

# ============================================================
# DRAMANOVA
# ============================================================

def dnv_dramas(lang="in", page=1, size=20):
    r = dx(f"{DNV_BASE}/api/v1/dramas", {"lang": lang, "page": page, "size": size}, AUTH_H)
    if r is None: return err("dramas", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("dramas", "dramanova", "response bukan dict")
    rows = r.get("rows", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "synopsis": clean(x.get("description", "")), "isCompleted": x.get("isCompleted", False), "viewCount": x.get("viewCount", 0), "categoryNames": x.get("categoryNames", []) or [], "platform": "dramanova"} for x in rows if isinstance(x, dict)]
    return ok("dramas", "dramanova", {"lang": lang, "page": page, "size": size, "items": dramas, "total": r.get("total", len(dramas)), "hasMore": len(dramas) >= size})

def dnv_detail(did, lang="in"):
    r = dx(f"{DNV_BASE}/api/v1/drama/{did}", {"lang": lang}, AUTH_H)
    if r is None: return err("detail", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("detail", "dramanova", "response bukan dict")
    eps_raw = r.get("episodes", []) or []; episodes = []
    for i, ep in enumerate(eps_raw):
        if not isinstance(ep, dict): continue
        subs = [{"lang": sub.get("lang", ""), "label": sub.get("label", ""), "url": sub.get("url", "")} for sub in (ep.get("subtitles", []) or []) if isinstance(sub, dict) and sub.get("url")]
        episodes.append({"episode": ep.get("number", i + 1), "id": str(ep.get("id", "")), "title": ep.get("title", f"Episode {i+1}"), "fileId": str(ep.get("fileId", "")), "cover": ep.get("cover", ""), "free": ep.get("free", False), "locked": not ep.get("free", False), "subtitles": subs})
    return ok("detail", "dramanova", {"data": {"id": str(r.get("id", did)), "title": r.get("title", ""), "cover": r.get("cover") or "", "banner": r.get("banner") or "", "synopsis": clean(r.get("description", "")), "totalEpisodes": r.get("totalEpisodes", len(episodes)), "isCompleted": r.get("isCompleted", False), "viewCount": r.get("viewCount", 0), "likeCount": r.get("likeCount", 0), "publishedAt": r.get("publishedAt", ""), "episodes": episodes, "platform": "dramanova"}})

def dnv_video(did, ep=1, lang="in"):
    detail_r = dx(f"{DNV_BASE}/api/v1/drama/{did}", {"lang": lang}, AUTH_H)
    if detail_r is None: return err("video", "dramanova", "gagal ambil detail")
    if not isinstance(detail_r, dict): return err("video", "dramanova", "detail bukan dict")
    eps_raw = detail_r.get("episodes", []) or []
    if not eps_raw: return err("video", "dramanova", "tidak ada episode")
    idx = min(ep - 1, len(eps_raw) - 1); target = eps_raw[idx]
    if not isinstance(target, dict): return err("video", "dramanova", "episode data invalid")
    file_id = str(target.get("fileId", ""))
    if not file_id: return err("video", "dramanova", f"fileId tidak ditemukan di episode {ep}")
    r = dx(f"{DNV_BASE}/api/video", {"id": file_id}, AUTH_H)
    if r is None: return err("video", "dramanova", "gagal request video")
    if not isinstance(r, dict): return err("video", "dramanova", "video response bukan dict")
    vids = r.get("videos", []) or []; quality_list = []
    for v in vids:
        if not isinstance(v, dict): continue
        main_url = v.get("main_url", ""); vid_type = "hls" if ".m3u8" in main_url else "mp4"
        quality_list.append({"label": v.get("definition", "auto"), "quality": v.get("quality", ""), "url": main_url, "backupUrl": v.get("backup_url", ""), "type": vid_type, "codec": v.get("codec", ""), "width": v.get("width", 0), "height": v.get("height", 0), "bitrate": v.get("bitrate", 0), "size": v.get("size", 0), "duration": v.get("duration", 0)})
    best_url = quality_list[-1]["url"] if quality_list else ""
    subs = [{"lang": sub.get("lang", ""), "label": sub.get("label", ""), "url": sub.get("url", "")} for sub in (target.get("subtitles", []) or []) if isinstance(sub, dict) and sub.get("url")]
    return ok("video", "dramanova", {"dramaId": did, "episode": target.get("number", idx + 1), "totalEps": len(eps_raw), "episodeId": str(target.get("id", "")), "fileId": file_id, "title": detail_r.get("title", ""), "epTitle": target.get("title", f"Episode {idx+1}"), "poster": r.get("poster", ""), "duration": r.get("duration", 0), "videoUrl": best_url, "subtitles": subs, "qualityList": quality_list, "free": target.get("free", False), "locked": not target.get("free", False), "platform": "dramanova"})

def dnv_search(kw, lang="in"):
    r = dx(f"{DNV_BASE}/api/v1/search", {"q": kw, "lang": lang}, AUTH_H)
    if r is None: return err("search", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("search", "dramanova", "response bukan dict")
    rows = r.get("rows", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "synopsis": clean(x.get("description", "")), "categoryNames": x.get("categoryNames", []) or [], "viewCount": x.get("viewCount", 0), "likeCount": x.get("likeCount", 0), "favoriteCount": x.get("favoriteCount", 0), "isCompleted": x.get("isCompleted", False), "publishedAt": x.get("publishedAt", ""), "platform": "dramanova"} for x in rows if isinstance(x, dict)]
    return ok("search", "dramanova", {"keyword": kw, "lang": lang, "items": dramas, "total": r.get("total", len(dramas))})

def dnv_modules(lang="in"):
    r = dx(f"{DNV_BASE}/api/v1/modules", {"lang": lang}, AUTH_H)
    if r is None: return err("modules", "dramanova", "gagal request")
    items = r if isinstance(r, list) else []
    modules = [{"categoryKey": x.get("categoryKey", ""), "categoryName": x.get("categoryName", ""), "dramaCount": x.get("dramaCount", 0)} for x in items if isinstance(x, dict)]
    return ok("modules", "dramanova", {"lang": lang, "modules": modules, "total": len(modules)})

def dnv_recommend(lang="in", category_key="dramanova_hot", page=1, size=5, limit=6):
    r = dx(f"{DNV_BASE}/api/v1/recommend", {"lang": lang, "categoryKey": category_key, "page": page, "size": size, "limit": limit}, AUTH_H)
    if r is None: return err("recommend", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("recommend", "dramanova", "response bukan dict")
    drama_list = r.get("dramas", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("title", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "viewCount": x.get("viewCount", 0), "platform": "dramanova"} for x in drama_list if isinstance(x, dict)]
    return ok("recommend", "dramanova", {"lang": lang, "category": r.get("category", category_key), "categoryKey": r.get("categoryKey", category_key), "page": page, "size": size, "limit": limit, "items": dramas, "total": len(dramas)})

# ============================================================
# LANDING PAGE HTML
# ============================================================

LANDING_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎬 DramaCina API</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎬</text></svg>">
<style>
*{margin:0;padding:0;box-sizing:border-box}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
body{font-family:'Inter',sans-serif;background:#0a0a0f;color:#e4e4e7;min-height:100vh;overflow-x:hidden}
.bg-grid{position:fixed;top:0;left:0;width:100%;height:100%;background-image:radial-gradient(circle at 1px 1px,rgba(255,255,255,.03) 1px,transparent 0);background-size:40px 40px;pointer-events:none;z-index:0}
.glow-1{position:fixed;top:-200px;right:-200px;width:600px;height:600px;background:radial-gradient(circle,rgba(139,92,246,.15),transparent 70%);border-radius:50%;pointer-events:none;z-index:0;animation:float 8s ease-in-out infinite}
.glow-2{position:fixed;bottom:-200px;left:-200px;width:500px;height:500px;background:radial-gradient(circle,rgba(236,72,153,.12),transparent 70%);border-radius:50%;pointer-events:none;z-index:0;animation:float 10s ease-in-out infinite reverse}
.glow-3{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:800px;height:800px;background:radial-gradient(circle,rgba(59,130,246,.08),transparent 70%);border-radius:50%;pointer-events:none;z-index:0;animation:float 12s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-30px) scale(1.05)}}
.container{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:20px}
header{text-align:center;padding:60px 20px 40px}
.logo{font-size:64px;margin-bottom:16px;animation:bounce 2s ease-in-out infinite}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
h1{font-size:42px;font-weight:800;background:linear-gradient(135deg,#8b5cf6,#ec4899,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;letter-spacing:-1px}
.subtitle{font-size:18px;color:#a1a1aa;font-weight:300;margin-bottom:12px}
.badge-row{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:20px}
.badge{padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600;letter-spacing:.5px;border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(10px)}
.badge-gs{background:rgba(139,92,246,.15);color:#a78bfa;border-color:rgba(139,92,246,.3)}
.badge-db{background:rgba(236,72,153,.15);color:#f472b6;border-color:rgba(236,72,153,.3)}
.badge-ml{background:rgba(59,130,246,.15);color:#60a5fa;border-color:rgba(59,130,246,.3)}
.badge-dbt{background:rgba(16,185,129,.15);color:#34d399;border-color:rgba(16,185,129,.3)}
.badge-dnv{background:rgba(245,158,11,.15);color:#fbbf24;border-color:rgba(245,158,11,.3)}
.stats{display:flex;gap:40px;justify-content:center;margin:30px 0;flex-wrap:wrap}
.stat{text-align:center}
.stat-num{font-size:32px;font-weight:800;background:linear-gradient(135deg,#8b5cf6,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stat-label{font-size:13px;color:#71717a;margin-top:4px;text-transform:uppercase;letter-spacing:1px}
.platforms{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:24px;margin-top:40px}
.platform{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:16px;overflow:hidden;transition:all .3s ease;position:relative}
.platform:hover{transform:translateY(-4px);border-color:rgba(255,255,255,.12);box-shadow:0 20px 60px rgba(0,0,0,.3)}
.platform::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:16px 16px 0 0}
.platform.gs::before{background:linear-gradient(90deg,#8b5cf6,#a78bfa)}
.platform.db::before{background:linear-gradient(90deg,#ec4899,#f472b6)}
.platform.ml::before{background:linear-gradient(90deg,#3b82f6,#60a5fa)}
.platform.dbt::before{background:linear-gradient(90deg,#10b981,#34d399)}
.platform.dnv::before{background:linear-gradient(90deg,#f59e0b,#fbbf24)}
.platform-header{padding:24px 24px 16px;display:flex;align-items:center;gap:14px}
.platform-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px}
.platform.gs .platform-icon{background:rgba(139,92,246,.15)}
.platform.db .platform-icon{background:rgba(236,72,153,.15)}
.platform.ml .platform-icon{background:rgba(59,130,246,.15)}
.platform.dbt .platform-icon{background:rgba(16,185,129,.15)}
.platform.dnv .platform-icon{background:rgba(245,158,11,.15)}
.platform-name{font-size:20px;font-weight:700;color:#fafafa}
.platform-desc{font-size:13px;color:#71717a;margin-top:2px}
.endpoints{padding:0 24px 24px}
.endpoint{display:flex;align-items:center;gap:10px;padding:10px 14px;margin:6px 0;border-radius:10px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);cursor:pointer;transition:all .2s ease;text-decoration:none;color:inherit}
.endpoint:hover{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.1);transform:translateX(4px)}
.method{font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;background:rgba(34,197,94,.15);color:#4ade80;letter-spacing:.5px;flex-shrink:0}
.ep-path{font-size:13px;color:#d4d4d8;font-family:'Courier New',monospace;font-weight:500;word-break:break-all}
.ep-params{font-size:11px;color:#71717a;font-family:'Courier New',monospace}
.try-btn{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:600;border:none;cursor:pointer;transition:all .2s ease;flex-shrink:0;text-decoration:none}
.platform.gs .try-btn{background:rgba(139,92,246,.15);color:#a78bfa}
.platform.db .try-btn{background:rgba(236,72,153,.15);color:#f472b6}
.platform.ml .try-btn{background:rgba(59,130,246,.15);color:#60a5fa}
.platform.dbt .try-btn{background:rgba(16,185,129,.15);color:#34d399}
.platform.dnv .try-btn{background:rgba(245,158,11,.15);color:#fbbf24}
.try-btn:hover{filter:brightness(1.3);transform:scale(1.05)}
footer{text-align:center;padding:60px 20px 40px;color:#52525b;font-size:13px}
footer a{color:#8b5cf6;text-decoration:none}
footer a:hover{text-decoration:underline}
.pulse{animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.uptime{display:inline-flex;align-items:center;gap:6px;padding:8px 20px;border-radius:20px;background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.2);color:#4ade80;font-size:13px;font-weight:500;margin-top:20px}
.uptime-dot{width:8px;height:8px;border-radius:50%;background:#4ade80;animation:pulse 1.5s ease-in-out infinite}
@media(max-width:768px){h1{font-size:28px}.subtitle{font-size:14px}.platforms{grid-template-columns:1fr}.stats{gap:20px}.stat-num{font-size:24px}header{padding:40px 16px 20px}.logo{font-size:48px}}
</style>
</head>
<body>
<div class="bg-grid"></div>
<div class="glow-1"></div>
<div class="glow-2"></div>
<div class="glow-3"></div>

<div class="container">
<header>
    <div class="logo">🎬</div>
    <h1>DramaCina API</h1>
    <p class="subtitle">Multi Platform Drama Streaming API Gateway</p>
    <div class="badge-row">
        <span class="badge badge-gs">GoodShort</span>
        <span class="badge badge-db">DramaBox</span>
        <span class="badge badge-ml">Melolo</span>
        <span class="badge badge-dbt">DramaBite</span>
        <span class="badge badge-dnv">DramaNova</span>
    </div>
    <div class="stats">
        <div class="stat"><div class="stat-num">5</div><div class="stat-label">Platforms</div></div>
        <div class="stat"><div class="stat-num">28</div><div class="stat-label">Endpoints</div></div>
        <div class="stat"><div class="stat-num">∞</div><div class="stat-label">Dramas</div></div>
    </div>
    <div class="uptime"><span class="uptime-dot"></span> API Online &bull; v2.0</div>
</header>

<div class="platforms">

    <!-- GoodShort -->
    <div class="platform gs">
        <div class="platform-header">
            <div class="platform-icon">📺</div>
            <div><div class="platform-name">GoodShort</div><div class="platform-desc">6 endpoints &bull; ID, PT, KR, TH</div></div>
        </div>
        <div class="endpoints">
            <a class="endpoint" href="/goodshort/home?page=1&channel=id" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/goodshort/home</div><div class="ep-params">?page=1&channel=id</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/goodshort/search?q=cinta" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/goodshort/search</div><div class="ep-params">?q=cinta</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/goodshort/detail?id=12345" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/goodshort/detail</div><div class="ep-params">?id=xxx</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/goodshort/stream?id=12345&ep=1&quality=720p" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/goodshort/stream</div><div class="ep-params">?id=xxx&ep=1&quality=720p</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/goodshort/stream_fast?id=12345&ep=1&quality=720p" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/goodshort/stream_fast</div><div class="ep-params">?id=xxx&ep=1&quality=720p</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/goodshort/unlock?id=12345&quality=720p" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/goodshort/unlock</div><div class="ep-params">?id=xxx&quality=720p</div></div>
                <span class="try-btn">Try →</span>
            </a>
        </div>
    </div>

    <!-- DramaBox -->
    <div class="platform db">
        <div class="platform-header">
            <div class="platform-icon">🎭</div>
            <div><div class="platform-name">DramaBox</div><div class="platform-desc">5 endpoints &bull; Multi language</div></div>
        </div>
        <div class="endpoints">
            <a class="endpoint" href="/dramabox/home?page=1&size=10&lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabox/home</div><div class="ep-params">?page=1&size=10&lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabox/rank?lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabox/rank</div><div class="ep-params">?lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabox/search?q=romance&lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabox/search</div><div class="ep-params">?q=romance&lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabox/detail?id=12345&lang=en" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabox/detail</div><div class="ep-params">?id=xxx&lang=en</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabox/episodes?id=12345&lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabox/episodes</div><div class="ep-params">?id=xxx&lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
        </div>
    </div>

    <!-- Melolo -->
    <div class="platform ml">
        <div class="platform-header">
            <div class="platform-icon">🎬</div>
            <div><div class="platform-name">Melolo</div><div class="platform-desc">4 endpoints &bull; Indonesian focus</div></div>
        </div>
        <div class="endpoints">
            <a class="endpoint" href="/melolo/home?lang=id&offset=0" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/melolo/home</div><div class="ep-params">?lang=id&offset=0</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/melolo/search?q=drama&lang=id" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/melolo/search</div><div class="ep-params">?q=drama&lang=id</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/melolo/detail?id=111&lang=id" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/melolo/detail</div><div class="ep-params">?id=xxx&lang=id</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/melolo/video?id=111&ep=1" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/melolo/video</div><div class="ep-params">?id=xxx&ep=1</div></div>
                <span class="try-btn">Try →</span>
            </a>
        </div>
    </div>

    <!-- DramaBite -->
    <div class="platform dbt">
        <div class="platform-header">
            <div class="platform-icon">🍿</div>
            <div><div class="platform-name">DramaBite</div><div class="platform-desc">8 endpoints &bull; Full featured</div></div>
        </div>
        <div class="endpoints">
            <a class="endpoint" href="/dramabite/dramas?lang=id&page=0" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/dramas</div><div class="ep-params">?lang=id&page=0</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/foryou?lang=id&page=0" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/foryou</div><div class="ep-params">?lang=id&page=0</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/hot?lang=id" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/hot</div><div class="ep-params">?lang=id</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/recommend?lang=id&page=0" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/recommend</div><div class="ep-params">?lang=id&page=0</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/search?q=love&lang=id&limit=20" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/search</div><div class="ep-params">?q=love&lang=id&limit=20</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/detail?id=222&lang=id" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/detail</div><div class="ep-params">?id=xxx&lang=id</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/likes?id=222&lang=id" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/likes</div><div class="ep-params">?id=xxx&lang=id</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramabite/episode?id=222&ep=1&lang=id&quality=default" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramabite/episode</div><div class="ep-params">?id=xxx&ep=1&quality=default</div></div>
                <span class="try-btn">Try →</span>
            </a>
        </div>
    </div>

    <!-- DramaNova -->
    <div class="platform dnv">
        <div class="platform-header">
            <div class="platform-icon">⭐</div>
            <div><div class="platform-name">DramaNova</div><div class="platform-desc">6 endpoints &bull; HD streaming</div></div>
        </div>
        <div class="endpoints">
            <a class="endpoint" href="/dramanova/dramas?lang=in&page=1&size=20" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramanova/dramas</div><div class="ep-params">?lang=in&page=1&size=20</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramanova/detail?id=333&lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramanova/detail</div><div class="ep-params">?id=xxx&lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramanova/video?id=333&ep=1&lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramanova/video</div><div class="ep-params">?id=xxx&ep=1&lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramanova/search?q=action&lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramanova/search</div><div class="ep-params">?q=action&lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramanova/modules?lang=in" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramanova/modules</div><div class="ep-params">?lang=in</div></div>
                <span class="try-btn">Try →</span>
            </a>
            <a class="endpoint" href="/dramanova/recommend?lang=in&category=dramanova_hot" target="_blank">
                <span class="method">GET</span>
                <div><div class="ep-path">/dramanova/recommend</div><div class="ep-params">?lang=in&category=dramanova_hot</div></div>
                <span class="try-btn">Try →</span>
            </a>
        </div>
    </div>

</div>

<footer>
    <p>Built with ❤️ by <a href="#">SanzzXD</a></p>
    <p style="margin-top:8px;font-size:12px;color:#3f3f46">DramaCina Multi Platform API &bull; v2.0 &bull; Powered by Vercel</p>
</footer>
</div>

<script>
document.querySelectorAll('.endpoint').forEach(el => {
    el.addEventListener('mouseenter', () => {
        el.style.transition = 'all 0.2s ease';
    });
});
document.querySelectorAll('.stat-num').forEach(el => {
    const target = el.textContent;
    if (target === '∞') return;
    const num = parseInt(target);
    let current = 0;
    const step = Math.ceil(num / 30);
    const timer = setInterval(() => {
        current += step;
        if (current >= num) { current = num; clearInterval(timer); }
        el.textContent = current;
    }, 30);
});
</script>
</body>
</html>"""

# ============================================================
# FLASK ROUTES
# ============================================================

# ── Landing Page ─────────────────────────────────────────────
@app.route("/")
def index():
    return Response(LANDING_HTML, mimetype="text/html")

# ── GoodShort ────────────────────────────────────────────────
@app.route("/goodshort/home")
def route_gs_home():
    return jsonify(gs_home(pi("page", 1), p("channel", "id")))

@app.route("/goodshort/search")
def route_gs_search():
    kw = p("q") or p("kw")
    if not kw: return jsonify(err("search", "goodshort", "param q wajib diisi"))
    return jsonify(gs_search(kw, pi("page", 1)))

@app.route("/goodshort/detail")
def route_gs_detail():
    bid = p("id")
    if not bid: return jsonify(err("detail", "goodshort", "param id wajib diisi"))
    return jsonify(gs_detail(bid))

@app.route("/goodshort/stream")
def route_gs_stream():
    bid = p("id")
    if not bid: return jsonify(err("stream", "goodshort", "param id wajib diisi"))
    return jsonify(gs_stream(bid, pi("ep", 1), p("quality", "720p")))

@app.route("/goodshort/stream_fast")
def route_gs_stream_fast():
    bid = p("id")
    if not bid: return jsonify(err("stream_fast", "goodshort", "param id wajib diisi"))
    return jsonify(gs_stream_fast(bid, pi("ep", 1), p("quality", "720p")))

@app.route("/goodshort/unlock")
def route_gs_unlock():
    bid = p("id")
    if not bid: return jsonify(err("unlock", "goodshort", "param id wajib diisi"))
    return jsonify(gs_unlock_all(bid, p("quality", "720p")))

# ── DramaBox ─────────────────────────────────────────────────
@app.route("/dramabox/home")
def route_db_home():
    return jsonify(db_home(pi("page", 1), pi("size", 10), p("lang", "in")))

@app.route("/dramabox/rank")
def route_db_rank():
    return jsonify(db_rank(p("lang", "in")))

@app.route("/dramabox/search")
def route_db_search():
    kw = p("q") or p("kw") or p("keyword")
    if not kw: return jsonify(err("search", "dramabox", "param q wajib diisi"))
    return jsonify(db_search(kw, pi("page", 1), p("lang", "in")))

@app.route("/dramabox/detail")
def route_db_detail():
    did = p("id")
    if not did: return jsonify(err("detail", "dramabox", "param id wajib diisi"))
    return jsonify(db_detail(did, p("lang", "en")))

@app.route("/dramabox/episodes")
def route_db_episodes():
    did = p("id")
    if not did: return jsonify(err("episodes", "dramabox", "param id wajib diisi"))
    return jsonify(db_episodes(did, p("lang", "in")))

# ── Melolo ───────────────────────────────────────────────────
@app.route("/melolo/home")
def route_ml_home():
    return jsonify(ml_home(p("lang", "id"), pi("offset", 0)))

@app.route("/melolo/search")
def route_ml_search():
    kw = p("q") or p("kw")
    if not kw: return jsonify(err("search", "melolo", "param q wajib diisi"))
    return jsonify(ml_search(kw, p("lang", "id")))

@app.route("/melolo/detail")
def route_ml_detail():
    did = p("id")
    if not did: return jsonify(err("detail", "melolo", "param id wajib diisi"))
    return jsonify(ml_detail(did, p("lang", "id")))

@app.route("/melolo/video")
def route_ml_video():
    did = p("id")
    if not did: return jsonify(err("video", "melolo", "param id wajib diisi"))
    return jsonify(ml_video(did, pi("ep", 1)))

# ── DramaBite ────────────────────────────────────────────────
@app.route("/dramabite/dramas")
def route_dbt_dramas():
    return jsonify(dbt_dramas(p("lang", "id"), pi("page", 0)))

@app.route("/dramabite/foryou")
def route_dbt_foryou():
    return jsonify(dbt_foryou(p("lang", "id"), pi("page", 0)))

@app.route("/dramabite/hot")
def route_dbt_hot():
    return jsonify(dbt_hot(p("lang", "id")))

@app.route("/dramabite/recommend")
def route_dbt_recommend():
    return jsonify(dbt_recommend(p("lang", "id"), pi("page", 0)))

@app.route("/dramabite/search")
def route_dbt_search():
    kw = p("q") or p("kw")
    if not kw: return jsonify(err("search", "dramabite", "param q wajib diisi"))
    return jsonify(dbt_search(kw, p("lang", "id"), pi("limit", 20)))

@app.route("/dramabite/detail")
def route_dbt_detail():
    did = p("id")
    if not did: return jsonify(err("detail", "dramabite", "param id wajib diisi"))
    return jsonify(dbt_detail(did, p("lang", "id")))

@app.route("/dramabite/likes")
def route_dbt_likes():
    did = p("id")
    if not did: return jsonify(err("likes", "dramabite", "param id wajib diisi"))
    return jsonify(dbt_likes(did, p("lang", "id")))

@app.route("/dramabite/episode")
def route_dbt_episode():
    did = p("id"); ep = pi("ep", 0)
    if not did: return jsonify(err("episode", "dramabite", "param id wajib diisi"))
    if not ep: return jsonify(err("episode", "dramabite", "param ep wajib diisi"))
    return jsonify(dbt_episode(did, ep, p("lang", "id"), p("quality", "default")))

# ── DramaNova ────────────────────────────────────────────────
@app.route("/dramanova/dramas")
def route_dnv_dramas():
    return jsonify(dnv_dramas(p("lang", "in"), pi("page", 1), pi("size", 20)))

@app.route("/dramanova/detail")
def route_dnv_detail():
    did = p("id")
    if not did: return jsonify(err("detail", "dramanova", "param id wajib diisi"))
    return jsonify(dnv_detail(did, p("lang", "in")))

@app.route("/dramanova/video")
def route_dnv_video():
    did = p("id")
    if not did: return jsonify(err("video", "dramanova", "param id wajib diisi"))
    return jsonify(dnv_video(did, pi("ep", 1), p("lang", "in")))

@app.route("/dramanova/search")
def route_dnv_search():
    kw = p("q") or p("kw")
    if not kw: return jsonify(err("search", "dramanova", "param q wajib diisi"))
    return jsonify(dnv_search(kw, p("lang", "in")))

@app.route("/dramanova/modules")
def route_dnv_modules():
    return jsonify(dnv_modules(p("lang", "in")))

@app.route("/dramanova/recommend")
def route_dnv_recommend():
    return jsonify(dnv_recommend(p("lang", "in"), p("category", "dramanova_hot"), pi("page", 1), pi("size", 5), pi("limit", 6)))
