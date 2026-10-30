#!/usr/bin/env python3
"""Coleta os feeds de todos.opml e grava um JSON com os itens da última semana.

Uso: python3 feeds/coletar.py [saida.json]

O Reddit limita acessos (HTTP 429), então as requisições são espaçadas e
repetidas com espera crescente. Feeds que falham entram em "falhas".
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

OPML = Path(__file__).with_name("todos.opml")
UA = "Mozilla/5.0 (radar-semanal; leitor RSS pessoal)"
INTERVALO = 10  # segundos entre feeds
ESPERAS_429 = [30, 60, 120]
MAX_ITENS = 15
JANELA = timedelta(days=8)
ATOM = "{http://www.w3.org/2005/Atom}"


def baixar(url):
    for espera in ESPERAS_429 + [None]:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or espera is None:
                raise
            time.sleep(espera)


def texto_limpo(html, limite=400):
    t = re.sub(r"<[^>]+>", " ", unescape(html or ""))
    t = re.sub(r"\s+", " ", t).strip()
    return t[:limite]


def data(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        try:
            return parsedate_to_datetime(valor)
        except (TypeError, ValueError):
            return None


def ler_itens(xml):
    raiz = ET.fromstring(xml)
    itens = []
    for e in raiz.iter(f"{ATOM}entry"):
        link = e.find(f"{ATOM}link")
        itens.append({
            "titulo": (e.findtext(f"{ATOM}title") or "").strip(),
            "link": link.get("href") if link is not None else "",
            "data": e.findtext(f"{ATOM}updated") or e.findtext(f"{ATOM}published"),
            "resumo": texto_limpo(e.findtext(f"{ATOM}content") or e.findtext(f"{ATOM}summary")),
        })
    for i in raiz.iter("item"):
        itens.append({
            "titulo": (i.findtext("title") or "").strip(),
            "link": i.findtext("link") or "",
            "data": i.findtext("pubDate"),
            "resumo": texto_limpo(i.findtext("description")),
        })
    return itens


def main():
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("radar.json")
    corte = datetime.now(timezone.utc) - JANELA
    resultado = {"gerado_em": datetime.now(timezone.utc).isoformat(), "pastas": {}, "falhas": []}
    corpo = ET.parse(OPML).getroot().find("body")
    for pasta in corpo:
        nome_pasta = pasta.get("text")
        for feed in pasta:
            nome, url = feed.get("text"), feed.get("xmlUrl")
            try:
                itens = ler_itens(baixar(url))
            except Exception as e:  # noqa: BLE001 — qualquer falha vira registro, não aborta
                resultado["falhas"].append({"feed": nome, "erro": str(e)})
                print(f"FALHA {nome}: {e}", file=sys.stderr)
            else:
                recentes = [i for i in itens if (d := data(i["data"])) is None or d >= corte]
                resultado["pastas"].setdefault(nome_pasta, {})[nome] = recentes[:MAX_ITENS]
                print(f"ok    {nome}: {len(recentes)} itens", file=sys.stderr)
            time.sleep(INTERVALO)
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1))
    print(f"{saida}: {len(resultado['falhas'])} falhas", file=sys.stderr)


if __name__ == "__main__":
    main()
