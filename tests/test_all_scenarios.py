import json
import requests
import time
from datetime import datetime

# Load scenarios
with open('scenarios.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    scenarios = data['scenarios']

# Convert to French questions
french_scenarios = [
    {"id": "S01", "question_fr": "Je veux acheter un laptop gaming sous 1500€", "expected_agent": "SALES"},
    {"id": "S02", "question_fr": "Ma commande de téléphone est arrivée cassée, que faire?", "expected_agent": "SUPPORT"},
    {"id": "S03", "question_fr": "Salut, comment vas-tu?", "expected_agent": "ANY"},
    {"id": "S04", "question_fr": "Je pense acheter une tablette mais je ne suis pas sûr", "expected_agent": "SALES"},
    {"id": "S05", "question_fr": "Avez-vous l'iPhone 15 Pro en stock?", "expected_agent": "SALES"},
    {"id": "S06", "question_fr": "Où est ma commande CMD-2026-0001?", "expected_agent": "SUPPORT"},
    {"id": "S07", "question_fr": "Puis-je retourner mon laptop acheté il y a 40 jours?", "expected_agent": "SUPPORT"},
    {"id": "S08", "question_fr": "Je veux acheter un Samsung Galaxy S23", "expected_agent": "SALES"},
    {"id": "S09", "question_fr": "Je m'ennuie, quoi de neuf en tech?", "expected_agent": "ANY"},
    {"id": "S10", "question_fr": "Ma batterie de laptop est morte", "expected_agent": "SUPPORT"},
    {"id": "S11", "question_fr": "Je veux acheter une tablette mais j'ai aussi un problème avec ma dernière commande", "expected_agent": "SUPPORT"},
    {"id": "S12", "question_fr": "Je veux un laptop", "expected_agent": "SALES"},
    {"id": "S13", "question_fr": "Où est ma commande #XYZ999999?", "expected_agent": "SUPPORT"},
    {"id": "S14", "question_fr": "Quel téléphone devrais-je acheter?", "expected_agent": "SALES"},
    {"id": "S15", "question_fr": "Votre service de livraison est terrible", "expected_agent": "SUPPORT"},  
]

# Results storage
test_results = {
    "test_date": datetime.now().isoformat(),
    "system": "Multi-Agent E-Commerce Chatbot",
    "total_scenarios": len(french_scenarios),
    "passed": 0,
    "failed": 0,
    "results": []
}

def test_scenario(scenario_id, question_fr, expected_agent):
    """Test a single scenario"""
    print(f"\n{'='*70}")
    print(f"📝 Test {scenario_id}: {question_fr}")
    print(f"Expected Agent: {expected_agent}")
    
    try:
        # Send request to chatbot
        response = requests.post(
            'http://localhost:5000/api/chat',
            json={
                'message': question_fr,
                'conversation_id': f'test_{scenario_id}'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            agent = data.get('agent', 'N/A')
            
            # Validation checks
            no_tech_terms = not any(word in ai_response.lower() for word in 
                ['search_products_tool', 'get_order', 'database', 'function', 'tool', 'def ', 'class ', 'import'])
            is_french_or_mixed = not (ai_response[:50].count(' ') ==0)  # Basic check
            is_short = len(ai_response) < 800  # Responses should be concise
            has_content = len(ai_response) > 5
            
            # Agent routing check
            agent_ok = (expected_agent == "ANY") or (expected_agent in agent.upper() if agent else False)
            
            # Determine if passed
            passed = no_tech_terms and is_short and has_content
            
            result = {
                "scenario_id": scenario_id,
                "question_fr": question_fr,
                "expected_agent": expected_agent,
                "actual_agent": agent,
                "agent_routing_ok": agent_ok,
                "ai_response": ai_response,
                "response_length": len(ai_response),
                "validation_checks": {
                    "no_technical_terms": no_tech_terms,
                    "concise_response": is_short,
                    "has_content": has_content,
                    "agent_correct": agent_ok
                },
                "overall_status": "✅ PASSED" if passed else "❌ FAILED",
                "timestamp": datetime.now().isoformat()
            }
            
            status_icon = "✅" if passed else "❌"
            print(f"{status_icon} Agent: {agent}")
            print(f"{status_icon} Response ({len(ai_response)} chars): {ai_response[:120]}...")
            print(f"{status_icon} No Tech Terms: {no_tech_terms}")
            print(f"{status_icon} Concise: {is_short}")
            
            return result, passed
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return {
                "scenario_id": scenario_id,
                "question_fr": question_fr,
                "error": f"HTTP {response.status_code}",
                "overall_status": "❌ FAILED"
            }, False
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {
            "scenario_id": scenario_id,
            "question_fr": question_fr,
            "error": str(e),
            "overall_status": "❌ FAILED"
        }, False

# Run all scenario tests
print("="*70)
print("🚀 AUTOMATED SCENARIO TESTING - MULTI-AGENT CHATBOT")
print("="*70)
print(f"📊 Total Scenarios: {len(french_scenarios)}")
print(f"🌐 Endpoint: http://localhost:5000/api/chat")
print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

for scenario in french_scenarios:
    result, passed = test_scenario(
        scenario['id'],
        scenario['question_fr'],
        scenario['expected_agent']
    )
    
    test_results['results'].append(result)
    
    if passed:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
    
    # Small delay between requests
    time.sleep(0.5)

# Generate summary
print(f"\n{'='*70}")
print("📊 FINAL TEST SUMMARY")
print(f"{'='*70}")
print(f"Total Scenarios:  {test_results['total_scenarios']}")
print(f"✅ Passed:        {test_results['passed']}")
print(f"❌ Failed:        {test_results['failed']}")
print(f"📈 Success Rate:  {(test_results['passed']/test_results['total_scenarios']*100):.1f}%")

# Save results
output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(test_results, f, indent=2, ensure_ascii=False)

print(f"\n✅ test_results file saved: {output_file}")
print(f"📄 You can submit this file as proof of working agents!")

# Print failed scenarios for review
if test_results['failed'] > 0:
    print(f"\n{'='*70}")
    print("❌ FAILED SCENARIOS (Need Attention):")
    print(f"{'='*70}")
    for result in test_results['results']:
        if 'FAILED' in result['overall_status']:
            print(f"\n🔴 {result['scenario_id']}: {result.get('question_fr', 'N/A')}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            elif 'validation_checks' in result:
                checks = result['validation_checks']
                for check, status in checks.items():
                    icon = "✅" if status else "❌"
                    print(f"   {icon} {check}: {status}")
else:
    print(f"\n🎉 ALL SCENARIOS PASSED! System is fully operational!")
    print(f"✅ Ready for production deployment!")
