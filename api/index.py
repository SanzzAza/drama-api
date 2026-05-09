#!/usr/bin/env python3
# api/index.py - DramaCina Multi Platform for Vercel

import requests
import json
import re
from flask import Flask, request, jsonify

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

GS_CHANNELS = {
    "id": 562,
    "pt": 564,
    "kr": 565,
    "th": 568,
}

s = requests.Session()
s.headers.update(HEADERS)

# ============================================================
# HELPERS
# ============================================================

def clean(t):
    return re.sub(r"<[^>]+>", "", str(t)).strip() if t else ""

def ok(action, source, result):
    return {
        "creator": "SanzzXD",
        "status": True,
        "code": 200,
        "action": action,
        "source": source,
        "result": result
    }

def err(action, source, msg):
    return {
        "creator": "SanzzXD",
        "status": False,
        "code": 400,
        "action": action,
        "source": source,
        "message": msg
    }

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
    r = dx(
        f"{GS_BASE}/api/v1/home",
        {"channelId": channel_id, "page": page, "pageSize": 12, "language": "id"},
        AUTH_H
    )
    if not r:
        return err("home", "goodshort", "gagal")
    data = r.get("data", {}) or {}
    records = data.get("records", []) or []
    sections = []
    flat_items = []
    seen = set()
    for rec in records:
        sec = {
            "channelId": rec.get("channelId", 0),
            "columnId": rec.get("columnId", 0),
            "name": rec.get("name", ""),
            "style": rec.get("style", ""),
            "more": rec.get("more", False),
            "items": []
        }
        for x in (rec.get("items", []) or []):
            bid = str(x.get("bookId") or x.get("action") or "")
            title = x.get("bookName") or x.get("name", "")
            cover = x.get("cover") or x.get("image", "")
            if not bid:
                continue
            item = {
                "id": bid, "title": title, "cover": cover,
                "image": x.get("image") or x.get("cover", ""),
                "introduction": clean(x.get("introduction", "")),
                "labels": x.get("labels", []) or [],
                "labelInfos": x.get("labelInfos", []) or [],
                "viewCount": x.get("viewCount", 0),
                "viewCountDisplay": x.get("viewCountDisplay", ""),
                "chapterCount": x.get("chapterCount", 0),
                "firstChapterId": x.get("firstChapterId", 0),
                "bookType": x.get("bookType", 0),
                "grade": x.get("grade", ""),
                "ratings": x.get("ratings", 0),
                "typeTwoNames": x.get("typeTwoNames", []) or [],
                "member": x.get("member", 0),
                "columnStyle": x.get("columnStyle", ""),
                "fullHDEnable": x.get("fullHDEnable", False),
                "downloadEnable": x.get("downloadEnable", False),
                "platform": "goodshort",
            }
            if x.get("scheduledReleaseDay"):
                item["scheduledReleaseDay"] = x["scheduledReleaseDay"]
            if x.get("scheduledReleaseDayOfTime"):
                item["scheduledReleaseDayOfTime"] = x["scheduledReleaseDayOfTime"]
            sec["items"].append(item)
            if bid not in seen and title:
                seen.add(bid)
                flat_items.append(item)
        sections.append(sec)
    return ok("home", "goodshort", {
        "page": data.get("current", page),
        "pageSize": data.get("size", 12),
        "totalSections": data.get("total", len(records)),
        "channelId": channel_id, "channel": channel,
        "sections": sections, "items": flat_items,
        "totalItems": len(flat_items),
    })

def gs_search(kw, page=1):
    r = dx(f"{GS_BASE}/api/v1/search", {"q": kw, "language": "id", "page": page, "pageSize": 20}, AUTH_H)
    if not r:
        return err("search", "goodshort", "gagal")
    sr = r.get("data", {}).get("searchResult", {})
    items = sr.get("records", []) if isinstance(sr, dict) else []
    dramas = []
    for x in items:
        dramas.append({
            "id": str(x.get("bookId", "")),
            "title": x.get("bookName") or x.get("name", ""),
            "cover": x.get("cover", ""),
            "introduction": clean(x.get("introduction", "")),
            "labels": x.get("labels", []) or [],
            "viewCount": x.get("viewCount", 0),
            "viewCountDisplay": x.get("viewCountDisplay", ""),
            "chapterCount": x.get("chapterCount", 0),
            "firstChapterId": x.get("firstChapterId", 0),
            "grade": x.get("grade", ""),
            "typeTwoNames": x.get("typeTwoNames", []) or [],
            "platform": "goodshort",
        })
    return ok("search", "goodshort", {"keyword": kw, "items": dramas, "total": len(dramas)})

def gs_detail(bid):
    r = dx(f"{GS_BASE}/api/v1/book/{bid}", {"language": "id"}, AUTH_H)
    if not r:
        return err("detail", "goodshort", "gagal")
    data = r.get("data", {}) or {}
    book = data.get("book", {}) or {}
    lst = data.get("list", []) or []
    episodes = []
    for i, ch in enumerate(lst):
        chapter_id = str(ch.get("id", ""))
        ql = []
        for mv in (ch.get("multiVideos", []) or []):
            cdn = mv.get("cdnList", []) or []
            q_url = cdn[0].get("videoPath", "") if cdn else mv.get("filePath", "")
            if q_url:
                ql.append({"label": mv.get("type", ""), "url": q_url, "type": "hls"})
        cdn_urls = [c.get("videoPath", "") for c in (ch.get("cdnList", []) or []) if c.get("videoPath")]
        episodes.append({
            "episode": i + 1, "chapterId": chapter_id,
            "title": ch.get("chapterName", f"Episode {i+1}"),
            "locked": bool(ch.get("charged", False)),
            "price": ch.get("price", 0), "free": ch.get("price", 0) == 0,
            "playTime": ch.get("playTime", 0), "playCount": ch.get("playCount", 0),
            "playCountDisplay": ch.get("playCountDisplay", ""),
            "image": ch.get("image", ""), "buyWay": ch.get("buyWay", ""),
            "payWay": ch.get("payWay", ""), "cdnUrl": ch.get("cdn", ""),
            "cdnUrls": cdn_urls, "qualities": ql,
        })
    return ok("detail", "goodshort", {"data": {
        "id": str(book.get("bookId", bid)), "title": book.get("bookName", ""),
        "cover": book.get("cover", ""), "detailCover": book.get("bookDetailCover", ""),
        "synopsis": clean(book.get("introduction", "")),
        "totalEpisodes": book.get("chapterCount", len(episodes)),
        "viewCount": book.get("viewCount", 0),
        "viewCountDisplay": book.get("viewCountDisplay", ""),
        "ratings": book.get("ratings", 0), "commentCount": book.get("commentCount", 0),
        "followCount": book.get("followCount", 0), "totalWords": book.get("totalWords", 0),
        "tags": book.get("labels", []), "labelInfos": book.get("labelInfos", []),
        "status": book.get("writeStatus", ""), "language": book.get("languageDisplay", ""),
        "unit": book.get("unit", ""), "grade": book.get("grade", ""),
        "freeEpisodes": book.get("free", 0), "memberEpisodes": book.get("member", 0),
        "producer": book.get("producer", ""), "playwright": book.get("playwright", ""),
        "protagonist": book.get("protagonist", ""), "pseudonym": book.get("pseudonym", ""),
        "fullHDEnable": book.get("fullHDEnable", False),
        "downloadEnable": book.get("downloadEnable", False),
        "episodes": episodes, "platform": "goodshort",
    }})

def gs_key(bid, chapter_id):
    r = dx(f"{GS_BASE}/api/v1/key", {"bookId": bid, "chapterId": chapter_id}, AUTH_H)
    if not r:
        return ""
    return r.get("key", "")

def gs_stream(bid, ep=1, quality="720p"):
    rd = dx(f"{GS_BASE}/api/v1/book/{bid}", {"language": "id"}, AUTH_H)
    if not rd:
        return err("stream", "goodshort", "gagal ambil detail")
    data = rd.get("data", {}) or {}
    book = data.get("book", {}) or {}
    lst = data.get("list", []) or []
    if not lst:
        return err("stream", "goodshort", "tidak ada episode")
    idx = min(ep - 1, len(lst) - 1)
    ch = lst[idx]
    chapter_id = str(ch.get("id", ""))
    if not chapter_id:
        return err("stream", "goodshort", "chapterId tidak ditemukan")
    rp = dx(f"{GS_BASE}/api/v1/play/{bid}/{chapter_id}", {"q": quality, "language": "id"}, AUTH_H)
    if not rp:
        return err("stream", "goodshort", "gagal ambil video")
    m3u8 = rp.get("m3u8", "")
    aes = gs_key(bid, chapter_id)
    ql = []
    for mv in (ch.get("multiVideos", []) or []):
        cdn = mv.get("cdnList", []) or []
        q_url = cdn[0].get("videoPath", "") if cdn else mv.get("filePath", "")
        if q_url:
            ql.append({"label": mv.get("type", ""), "url": q_url, "type": "hls"})
    if not ql and m3u8:
        ql.append({"label": quality, "url": m3u8, "type": "hls"})
    return ok("stream", "goodshort", {
        "bookId": bid, "chapterId": chapter_id, "episode": idx + 1,
        "totalEps": len(lst), "title": book.get("bookName", ""),
        "epTitle": ch.get("chapterName", f"Episode {idx+1}"),
        "videoUrl": m3u8, "quality": quality, "aesKey": aes,
        "kEncrypted": rp.get("k", ""), "sSeed": rp.get("s", ""),
        "isLocked": bool(ch.get("charged", False)),
        "isFree": not bool(ch.get("charged", False)),
        "qualityList": ql,
    })

def gs_stream_fast(bid, ep=1, quality="720p"):
    r = dx(f"{GS_BASE}/api/v1/unlock/{bid}", {"q": quality}, AUTH_H)
    if not r:
        return err("stream_fast", "goodshort", "gagal unlock")
    videos = r.get("videos", []) or []
    total = r.get("total", len(videos))
    if not videos:
        return err("stream_fast", "goodshort", "tidak ada episode")
    idx = min(ep - 1, len(videos) - 1)
    target = videos[idx]
    chapter_id = str(target.get("id", ""))
    url = target.get("url", "")
    aes = gs_key(bid, chapter_id) if chapter_id else ""
    all_eps = []
    for i, v in enumerate(videos):
        all_eps.append({
            "episode": i + 1, "chapterId": str(v.get("id", "")),
            "name": v.get("name", ""), "url": v.get("url", ""), "type": "hls"
        })
    return ok("stream_fast", "goodshort", {
        "bookId": bid, "chapterId": chapter_id, "episode": idx + 1,
        "totalEps": total, "videoUrl": url, "quality": quality, "aesKey": aes,
        "qualityList": [{"label": quality, "url": url, "type": "hls"}] if url else [],
        "allEpisodes": all_eps,
    })

def gs_unlock_all(bid, quality="720p"):
    r = dx(f"{GS_BASE}/api/v1/unlock/{bid}", {"q": quality}, AUTH_H)
    if not r:
        return err("unlock", "goodshort", "gagal")
    videos = r.get("videos", []) or []
    episodes = []
    for i, v in enumerate(videos):
        episodes.append({
            "episode": i + 1, "chapterId": str(v.get("id", "")),
            "name": v.get("name", ""), "url": v.get("url", ""), "type": "hls"
        })
    return ok("unlock", "goodshort", {
        "bookId": bid, "quality": quality,
        "total": r.get("total", len(videos)), "episodes": episodes,
    })

# ============================================================
# DRAMABOX
# ============================================================

def db_home(page=1, size=10, lang="in"):
    r = dx(f"{DB_BASE}/api/home", {"page": page, "size": size, "lang": lang}, AUTH_H)
    if not r:
        return err("home", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {})
    sections_raw = root.get("sections", []) or []
    sections = []
    flat_items = []
    seen = set()
    for sec in sections_raw:
        books = sec.get("books", []) or []
        parsed_books = []
        for b in books:
            item = {
                "id": str(b.get("bookId", "")), "title": b.get("bookName", ""),
                "cover": b.get("coverWap", ""), "episodes": b.get("chapterCount", 0),
                "synopsis": clean(b.get("introduction", "")),
                "tags": b.get("tags", []) or [], "tagV3s": b.get("tagV3s", []) or [],
                "isEntry": b.get("isEntry", 0), "index": b.get("index", 0),
                "corner": b.get("corner", {}), "dataFrom": b.get("dataFrom", ""),
                "cardType": b.get("cardType", 0),
                "markNamesConnectKey": b.get("markNamesConnectKey", ""),
                "playCount": b.get("playCount", ""),
                "bookShelfTime": b.get("bookShelfTime", 0),
                "shelfTime": b.get("shelfTime", ""),
                "inLibrary": b.get("inLibrary", False), "platform": "dramabox"
            }
            parsed_books.append(item)
            if item["id"] and item["id"] not in seen:
                seen.add(item["id"])
                flat_items.append(item)
        sections.append({
            "id": sec.get("id", 0), "title": sec.get("title", ""),
            "subTitle": sec.get("subTitle", ""), "style": sec.get("style", ""),
            "type": sec.get("type", ""), "books": parsed_books
        })
    return ok("home", "dramabox", {
        "code": r.get("code", 0), "message": r.get("message", ""),
        "page": page, "size": size, "lang": lang,
        "sections": sections, "items": flat_items,
        "totalSections": len(sections), "totalItems": len(flat_items)
    })

def db_rank(lang="in"):
    r = dx(f"{DB_BASE}/api/rank", {"lang": lang}, AUTH_H)
    if not r:
        return err("rank", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {})
    rank_types = root.get("rankTypeVoList", []) or []
    rank_list = root.get("rankList", []) or []
    items = []
    for x in rank_list:
        items.append({
            "id": str(x.get("bookId", "")), "title": x.get("bookName", ""),
            "cover": x.get("coverWap", ""), "episodes": x.get("chapterCount", 0),
            "synopsis": clean(x.get("introduction", "")),
            "tags": x.get("tags", []) or [], "tagV3s": x.get("tagV3s", []) or [],
            "isEntry": x.get("isEntry", 0), "index": x.get("index", 0),
            "protagonist": x.get("protagonist", ""), "dataFrom": x.get("dataFrom", ""),
            "cardType": x.get("cardType", 0), "rankVo": x.get("rankVo", {}),
            "markNamesConnectKey": x.get("markNamesConnectKey", ""),
            "playCount": x.get("playCount", ""),
            "bookShelfTime": x.get("bookShelfTime", 0),
            "shelfTime": x.get("shelfTime", ""), "corner": x.get("corner", {}),
            "inLibrary": x.get("inLibrary", False), "platform": "dramabox"
        })
    return ok("rank", "dramabox", {
        "code": r.get("code", 0), "message": r.get("message", ""),
        "lang": lang, "rankTypes": rank_types, "items": items, "total": len(items)
    })

def db_search(keyword, page=1, lang="in"):
    r = dx(f"{DB_BASE}/api/search", {"keyword": keyword, "page": page, "lang": lang}, AUTH_H)
    if not r:
        return err("search", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {})
    search_list = root.get("searchList", []) or []
    items = []
    for x in search_list:
        items.append({
            "id": str(x.get("bookId", "")), "title": x.get("bookName", ""),
            "cover": x.get("cover", ""), "synopsis": clean(x.get("introduction", "")),
            "author": x.get("author", ""), "inLibraryCount": x.get("inLibraryCount", 0),
            "bookSource": x.get("bookSource", {}), "playCount": x.get("playCount", ""),
            "sort": x.get("sort", 0), "protagonist": x.get("protagonist", ""),
            "tagNames": x.get("tagNames", []) or [], "corner": x.get("corner", {}),
            "markNamesConnectKey": x.get("markNamesConnectKey", ""),
            "algorithmRecomDot": x.get("algorithmRecomDot", ""),
            "inLibrary": x.get("inLibrary", False), "platform": "dramabox"
        })
    return ok("search", "dramabox", {
        "code": r.get("code", 0), "message": r.get("message", ""),
        "keyword": root.get("keyword", keyword), "page": page, "lang": lang,
        "items": items, "total": len(items)
    })

def db_detail(did, lang="en"):
    r = dx(f"{DB_BASE}/api/drama/{did}", {"lang": lang}, AUTH_H)
    if not r:
        return err("detail", "dramabox", "gagal")
    root = r.get("data", {}).get("data", {})
    lst = root.get("list", []) or []
    episodes = []
    for i, ch in enumerate(lst):
        episodes.append({
            "episode": i + 1, "chapterId": str(ch.get("chapterId", "")),
            "chapterIndex": ch.get("chapterIndex", i),
            "isCharge": ch.get("isCharge", 0), "isPay": ch.get("isPay", 0),
            "chapterSizeVoList": ch.get("chapterSizeVoList", []) or []
        })
    return ok("detail", "dramabox", {
        "code": r.get("code", 0), "message": r.get("message", ""),
        "data": {
            "id": str(root.get("bookId", did)), "title": root.get("bookName", ""),
            "cover": root.get("coverWap", "") or root.get("cover", ""),
            "synopsis": clean(root.get("introduction", "")) or clean(root.get("description", "")),
            "bookStatus": root.get("bookStatus", 0), "corner": root.get("corner", {}),
            "crossChapter": root.get("crossChapter", False),
            "crossChapterTips": root.get("crossChapterTips", ""),
            "episodes": episodes, "totalEpisodes": len(episodes), "platform": "dramabox"
        }
    })

def db_episodes(did, lang="in"):
    r = dx(f"{DB_BASE}/api/drama/{did}/episodes", {"lang": lang}, AUTH_H)
    if not r:
        return err("episodes", "dramabox", "gagal")
    root = r.get("data", {})
    eps = root.get("episodes", []) or []
    episodes = []
    for e in eps:
        qlabel = f'{e.get("quality", "Auto")}p' if isinstance(e.get("quality"), int) else str(e.get("quality", "Auto"))
        ql = []
        if e.get("url"):
            ql.append({"label": qlabel, "url": e.get("url", ""), "type": "mp4"})
        episodes.append({
            "episode": e.get("episode", 0), "chapterId": str(e.get("chapterId", "")),
            "chapterName": e.get("chapterName", ""), "cover": e.get("cover", ""),
            "quality": e.get("quality", 0), "url": e.get("url", ""),
            "subtitles": e.get("subtitles", []) or [], "qualityList": ql
        })
    return ok("episodes", "dramabox", {
        "code": r.get("code", 0), "message": r.get("message", ""),
        "bookId": root.get("bookId", did), "bookName": root.get("bookName", ""),
        "cover": root.get("cover", ""), "description": clean(root.get("description", "")),
        "totalEpisodes": root.get("totalEpisodes", len(episodes)),
        "quality": root.get("quality", 0), "episodes": episodes, "platform": "dramabox"
    })

# ============================================================
# MELOLO
# ============================================================

def ml_home(lang="id", offset=0):
    r = dx(f"{ML_BASE}/api/home", {"lang": lang, "offset": offset}, ML_H)
    if not r or r.get("code") != 0:
        return err("home", "melolo", "gagal")
    items = r.get("data", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("name", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "synopsis": clean(x.get("intro", "")), "platform": "melolo"} for x in items]
    return ok("home", "melolo", {"lang": lang, "offset": offset, "items": dramas, "total": len(dramas)})

def ml_search(kw, lang="id"):
    r = dx(f"{ML_BASE}/api/search", {"q": kw, "lang": lang}, ML_H)
    if not r or r.get("code") != 0:
        return err("search", "melolo", "gagal")
    items = r.get("data", []) or []
    dramas = [{"id": str(x.get("id", "")), "title": x.get("name", ""), "cover": x.get("cover", ""), "episodes": x.get("episodes", 0), "synopsis": clean(x.get("intro", "")), "author": x.get("author", ""), "platform": "melolo"} for x in items]
    return ok("search", "melolo", {"keyword": kw, "lang": lang, "count": r.get("count", len(dramas)), "items": dramas, "total": len(dramas)})

def ml_detail(did, lang="id"):
    r = dx(f"{ML_BASE}/api/detail/{did}", {"lang": lang}, ML_H)
    if not r or r.get("code") != 0:
        return err("detail", "melolo", "gagal")
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
                    if vid and vid not in candidate_ids:
                        candidate_ids.append(vid)
                    break
        last_error = "gagal"
        for current_id in candidate_ids:
            h = {**HEADERS, **ML_H}
            r = s.get(f"{ML_BASE}/api/video", params={"id": current_id, "ep": ep, "code": TOKEN_ML}, headers=h, timeout=20)
            if r.status_code != 200:
                last_error = f"HTTP {r.status_code}"
                continue
            try:
                data = r.json()
            except:
                last_error = "response bukan json"
                continue
            if data.get("code") != 200:
                last_error = data.get("msg") or data.get("message") or f"code={data.get('code')}"
                continue
            ql = data.get("qualityList", []) or []
            quality_list = [{"label": q.get("label", ""), "url": q.get("url", ""), "type": "mp4"} for q in ql]
            return ok("video", "melolo", {
                "dramaId": did, "usedId": current_id,
                "episode": data.get("episodeNumber", ep),
                "number": data.get("number", ep),
                "videoUrl": data.get("videoUrl", ""),
                "locked": data.get("locked", False),
                "qualityList": quality_list, "platform": "melolo"
            })
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
    video_url = r.get("video", "")
    vid_type = "hls" if ".m3u8" in video_url else "mp4" if ".mp4" in video_url else "hls"
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
    dramas = []
    for x in rows:
        if not isinstance(x, dict): continue
        dramas.append({
            "id": str(x.get("id", "")), "title": x.get("title", ""),
            "cover": x.get("cover", ""), "episodes": x.get("episodes", 0),
            "synopsis": clean(x.get("description", "")),
            "isCompleted": x.get("isCompleted", False),
            "viewCount": x.get("viewCount", 0),
            "categoryNames": x.get("categoryNames", []) or [],
            "platform": "dramanova",
        })
    return ok("dramas", "dramanova", {
        "lang": lang, "page": page, "size": size,
        "items": dramas, "total": r.get("total", len(dramas)),
        "hasMore": len(dramas) >= size,
    })

def dnv_detail(did, lang="in"):
    r = dx(f"{DNV_BASE}/api/v1/drama/{did}", {"lang": lang}, AUTH_H)
    if r is None: return err("detail", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("detail", "dramanova", "response bukan dict")
    eps_raw = r.get("episodes", []) or []
    episodes = []
    for i, ep in enumerate(eps_raw):
        if not isinstance(ep, dict): continue
        subs = []
        for sub in (ep.get("subtitles", []) or []):
            if isinstance(sub, dict) and sub.get("url"):
                subs.append({"lang": sub.get("lang", ""), "label": sub.get("label", ""), "url": sub.get("url", "")})
        episodes.append({
            "episode": ep.get("number", i + 1), "id": str(ep.get("id", "")),
            "title": ep.get("title", f"Episode {i+1}"), "fileId": str(ep.get("fileId", "")),
            "cover": ep.get("cover", ""), "free": ep.get("free", False),
            "locked": not ep.get("free", False), "subtitles": subs,
        })
    return ok("detail", "dramanova", {"data": {
        "id": str(r.get("id", did)), "title": r.get("title", ""),
        "cover": r.get("cover") or "", "banner": r.get("banner") or "",
        "synopsis": clean(r.get("description", "")),
        "totalEpisodes": r.get("totalEpisodes", len(episodes)),
        "isCompleted": r.get("isCompleted", False),
        "viewCount": r.get("viewCount", 0), "likeCount": r.get("likeCount", 0),
        "publishedAt": r.get("publishedAt", ""),
        "episodes": episodes, "platform": "dramanova",
    }})

def dnv_video(did, ep=1, lang="in"):
    detail_r = dx(f"{DNV_BASE}/api/v1/drama/{did}", {"lang": lang}, AUTH_H)
    if detail_r is None: return err("video", "dramanova", "gagal ambil detail")
    if not isinstance(detail_r, dict): return err("video", "dramanova", "detail bukan dict")
    eps_raw = detail_r.get("episodes", []) or []
    if not eps_raw: return err("video", "dramanova", "tidak ada episode")
    idx = min(ep - 1, len(eps_raw) - 1)
    target = eps_raw[idx]
    if not isinstance(target, dict): return err("video", "dramanova", "episode data invalid")
    file_id = str(target.get("fileId", ""))
    if not file_id: return err("video", "dramanova", f"fileId tidak ditemukan di episode {ep}")
    r = dx(f"{DNV_BASE}/api/video", {"id": file_id}, AUTH_H)
    if r is None: return err("video", "dramanova", "gagal request video")
    if not isinstance(r, dict): return err("video", "dramanova", "video response bukan dict")
    vids = r.get("videos", []) or []
    quality_list = []
    for v in vids:
        if not isinstance(v, dict): continue
        main_url = v.get("main_url", "")
        backup_url = v.get("backup_url", "")
        vid_type = "hls" if ".m3u8" in main_url else "mp4"
        quality_list.append({
            "label": v.get("definition", "auto"), "quality": v.get("quality", ""),
            "url": main_url, "backupUrl": backup_url, "type": vid_type,
            "codec": v.get("codec", ""), "width": v.get("width", 0),
            "height": v.get("height", 0), "bitrate": v.get("bitrate", 0),
            "size": v.get("size", 0), "duration": v.get("duration", 0),
        })
    best_url = quality_list[-1]["url"] if quality_list else ""
    subs = []
    for sub in (target.get("subtitles", []) or []):
        if isinstance(sub, dict) and sub.get("url"):
            subs.append({"lang": sub.get("lang", ""), "label": sub.get("label", ""), "url": sub.get("url", "")})
    return ok("video", "dramanova", {
        "dramaId": did, "episode": target.get("number", idx + 1),
        "totalEps": len(eps_raw), "episodeId": str(target.get("id", "")),
        "fileId": file_id, "title": detail_r.get("title", ""),
        "epTitle": target.get("title", f"Episode {idx+1}"),
        "poster": r.get("poster", ""), "duration": r.get("duration", 0),
        "videoUrl": best_url, "subtitles": subs, "qualityList": quality_list,
        "free": target.get("free", False), "locked": not target.get("free", False),
        "platform": "dramanova",
    })

def dnv_search(kw, lang="in"):
    r = dx(f"{DNV_BASE}/api/v1/search", {"q": kw, "lang": lang}, AUTH_H)
    if r is None: return err("search", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("search", "dramanova", "response bukan dict")
    rows = r.get("rows", []) or []
    dramas = []
    for x in rows:
        if not isinstance(x, dict): continue
        dramas.append({
            "id": str(x.get("id", "")), "title": x.get("title", ""),
            "cover": x.get("cover", ""), "episodes": x.get("episodes", 0),
            "synopsis": clean(x.get("description", "")),
            "categoryNames": x.get("categoryNames", []) or [],
            "viewCount": x.get("viewCount", 0), "likeCount": x.get("likeCount", 0),
            "favoriteCount": x.get("favoriteCount", 0),
            "isCompleted": x.get("isCompleted", False),
            "publishedAt": x.get("publishedAt", ""), "platform": "dramanova",
        })
    return ok("search", "dramanova", {"keyword": kw, "lang": lang, "items": dramas, "total": r.get("total", len(dramas))})

def dnv_modules(lang="in"):
    r = dx(f"{DNV_BASE}/api/v1/modules", {"lang": lang}, AUTH_H)
    if r is None: return err("modules", "dramanova", "gagal request")
    items = r if isinstance(r, list) else []
    modules = []
    for x in items:
        if not isinstance(x, dict): continue
        modules.append({
            "categoryKey": x.get("categoryKey", ""),
            "categoryName": x.get("categoryName", ""),
            "dramaCount": x.get("dramaCount", 0),
        })
    return ok("modules", "dramanova", {"lang": lang, "modules": modules, "total": len(modules)})

def dnv_recommend(lang="in", category_key="dramanova_hot", page=1, size=5, limit=6):
    r = dx(f"{DNV_BASE}/api/v1/recommend", {"lang": lang, "categoryKey": category_key, "page": page, "size": size, "limit": limit}, AUTH_H)
    if r is None: return err("recommend", "dramanova", "gagal request")
    if not isinstance(r, dict): return err("recommend", "dramanova", "response bukan dict")
    drama_list = r.get("dramas", []) or []
    dramas = []
    for x in drama_list:
        if not isinstance(x, dict): continue
        dramas.append({
            "id": str(x.get("id", "")), "title": x.get("title", ""),
            "cover": x.get("cover", ""), "episodes": x.get("episodes", 0),
            "viewCount": x.get("viewCount", 0), "platform": "dramanova",
        })
    return ok("recommend", "dramanova", {
        "lang": lang, "category": r.get("category", category_key),
        "categoryKey": r.get("categoryKey", category_key),
        "page": page, "size": size, "limit": limit,
        "items": dramas, "total": len(dramas),
    })

# ============================================================
# FLASK ROUTES
# ============================================================

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
    did = p("id")
    ep  = pi("ep", 0)
    if not did: return jsonify(err("episode", "dramabite", "param id wajib diisi"))
    if not ep:  return jsonify(err("episode", "dramabite", "param ep wajib diisi"))
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
    return jsonify(dnv_recommend(
        p("lang", "in"), p("category", "dramanova_hot"),
        pi("page", 1), pi("size", 5), pi("limit", 6)
    ))

# ── Index ────────────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "creator": "SanzzXD",
        "status": True,
        "description": "DramaCina Multi Platform API",
        "routes": {
            "goodshort": [
                "/goodshort/home?page=1&channel=id",
                "/goodshort/search?q=keyword",
                "/goodshort/detail?id=xxx",
                "/goodshort/stream?id=xxx&ep=1&quality=720p",
                "/goodshort/stream_fast?id=xxx&ep=1&quality=720p",
                "/goodshort/unlock?id=xxx&quality=720p",
            ],
            "dramabox": [
                "/dramabox/home?page=1&size=10&lang=in",
                "/dramabox/rank?lang=in",
                "/dramabox/search?q=keyword&lang=in",
                "/dramabox/detail?id=xxx&lang=en",
                "/dramabox/episodes?id=xxx&lang=in",
            ],
            "melolo": [
                "/melolo/home?lang=id&offset=0",
                "/melolo/search?q=keyword&lang=id",
                "/melolo/detail?id=xxx&lang=id",
                "/melolo/video?id=xxx&ep=1",
            ],
            "dramabite": [
                "/dramabite/dramas?lang=id&page=0",
                "/dramabite/foryou?lang=id&page=0",
                "/dramabite/hot?lang=id",
                "/dramabite/recommend?lang=id&page=0",
                "/dramabite/search?q=keyword&lang=id&limit=20",
                "/dramabite/detail?id=xxx&lang=id",
                "/dramabite/likes?id=xxx&lang=id",
                "/dramabite/episode?id=xxx&ep=1&lang=id&quality=default",
            ],
            "dramanova": [
                "/dramanova/dramas?lang=in&page=1&size=20",
                "/dramanova/detail?id=xxx&lang=in",
                "/dramanova/video?id=xxx&ep=1&lang=in",
                "/dramanova/search?q=keyword&lang=in",
                "/dramanova/modules?lang=in",
                "/dramanova/recommend?lang=in&category=dramanova_hot&page=1&size=5&limit=6",
            ],
        }
    })

# ── Vercel handler ───────────────────────────────────────────
# Vercel butuh variable bernama 'app' - sudah ada di atas
