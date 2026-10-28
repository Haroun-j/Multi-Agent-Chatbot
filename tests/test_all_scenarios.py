"""
Runs the 15 scripted scenarios against a running server and checks, for each
answer, that the orchestrator picked the expected agent and that the reply is
short, non-empty and free of technical vocabulary.

Needs the full stack (MariaDB up, GROQ_API_KEY set, `python server.py`).

    python tests/test_all_scenarios.py [--url http://localhost:5000]

Results are written to tests/results/<timestamp>.json. The script exits with
code 1 if any scenario fails.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

import requests

HERE = os.path.dirname(os.path.abspath(__file__))

# French single-turn versions of tests/scenarios.json. "ANY" means the routing
# is not checked (small talk can legitimately go to GENERAL or to an agent).
SCENARIOS = [
    {"id": "S01", "question": "Je veux acheter un laptop gaming sous 1500€", "expected_agent": "SALES"},
    {"id": "S02", "question": "Ma commande de téléphone est arrivée cassée, que faire?", "expected_agent": "SUPPORT"},
    {"id": "S03", "question": "Salut, comment vas-tu?", "expected_agent": "ANY"},
    {"id": "S04", "question": "Je pense acheter une tablette mais je ne suis pas sûr", "expected_agent": "SALES"},
    {"id": "S05", "question": "Avez-vous l'iPhone 15 Pro en stock?", "expected_agent": "SALES"},
    {"id": "S06", "question": "Où est ma commande CMD-2026-0001?", "expected_agent": "SUPPORT"},
    {"id": "S07", "question": "Puis-je retourner mon laptop acheté il y a 40 jours?", "expected_agent": "SUPPORT"},
    {"id": "S08", "question": "Je veux acheter un Samsung Galaxy S23", "expected_agent": "SALES"},
    {"id": "S09", "question": "Je m'ennuie, quoi de neuf en tech?", "expected_agent": "ANY"},
    {"id": "S10", "question": "Ma batterie de laptop est morte", "expected_agent": "SUPPORT"},
    {"id": "S11", "question": "Je veux acheter une tablette mais j'ai aussi un problème avec ma dernière commande", "expected_agent": "SUPPORT"},
    {"id": "S12", "question": "Je veux un laptop", "expected_agent": "SALES"},
    {"id": "S13", "question": "Où est ma commande #XYZ999999?", "expected_agent": "SUPPORT"},
    {"id": "S14", "question": "Quel téléphone devrais-je acheter?", "expected_agent": "SALES"},
    {"id": "S15", "question": "Votre service de livraison est terrible", "expected_agent": "SUPPORT"},
]

# Words a customer should never see in an answer.
TECHNICAL_TERMS = re.compile(
    r"\b(tool|tools|function|fonction|database|sql|json|api)\b|_tool\b|\bget_[a-z_]+",
    re.IGNORECASE,
)


def check_answer(scenario, data):
    answer = data.get("response", "") or ""
    agent = (data.get("agent") or "").upper()
    return {
        "has_content": len(answer) > 5,
        "concise": len(answer) < 800,
        "no_technical_terms": TECHNICAL_TERMS.search(answer) is None,
        "agent_correct": scenario["expected_agent"] == "ANY" or agent == scenario["expected_agent"],
    }


def run_scenario(base_url, scenario):
    print(f"\n{scenario['id']}: {scenario['question']}  (expected: {scenario['expected_agent']})")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": scenario["question"], "conversation_id": f"test_{scenario['id']}"},
            timeout=60,
        )
    except requests.RequestException as exc:
        print(f"  request failed: {exc}")
        return {"scenario_id": scenario["id"], "error": str(exc), "passed": False}

    if response.status_code != 200:
        print(f"  HTTP {response.status_code}: {response.text[:200]}")
        return {"scenario_id": scenario["id"], "error": f"HTTP {response.status_code}", "passed": False}

    data = response.json()
    checks = check_answer(scenario, data)
    passed = all(checks.values())
    print(f"  agent: {data.get('agent')}  tools: {', '.join(data.get('tools_used') or []) or '-'}")
    print(f"  answer: {data.get('response', '')[:150]}")
    print(f"  {'PASS' if passed else 'FAIL'}  " + "  ".join(f"{k}={v}" for k, v in checks.items()))
    return {
        "scenario_id": scenario["id"],
        "question": scenario["question"],
        "expected_agent": scenario["expected_agent"],
        "actual_agent": data.get("agent"),
        "tools_used": data.get("tools_used", []),
        "answer": data.get("response"),
        "checks": checks,
        "passed": passed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default=os.getenv("CHATBOT_URL", "http://localhost:5000"))
    parser.add_argument("--delay", type=float, default=0.5, help="pause between requests (seconds)")
    args = parser.parse_args()

    results = []
    for scenario in SCENARIOS:
        results.append(run_scenario(args.url, scenario))
        time.sleep(args.delay)

    passed = sum(1 for r in results if r["passed"])
    routing_checked = [r for r in results if "checks" in r and r["expected_agent"] != "ANY"]
    routing_ok = sum(1 for r in routing_checked if r["checks"]["agent_correct"])

    print("\n" + "=" * 60)
    print(f"Scenarios passed: {passed}/{len(results)}")
    print(f"Routing correct:  {routing_ok}/{len(routing_checked)} (scenarios with an expected agent)")

    out_dir = os.path.join(HERE, "results")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "url": args.url,
            "passed": passed,
            "total": len(results),
            "routing_correct": routing_ok,
            "routing_checked": len(routing_checked),
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"Details written to {out_file}")

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
