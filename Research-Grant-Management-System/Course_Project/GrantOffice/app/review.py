"""Human assessments tied to the proposal snapshot that was reviewed."""
from . import store


def draft_hash(state):
    return store.digest({
        'plan': state['plan'], 'narrative': state.get('narrative', ''),
        'call': state.get('selected_call', {}), 'literature': state.get('literature', []),
        'evidence': state.get('evidence', []),
    })


def assessments(state):
    return store.registry_item('draft_reviews', state['run_id'] + ':' + draft_hash(state)) or {}


def eligibility_checks(state, evidence, reviews):
    call = state.get('selected_call', {})
    rules = call.get('eligibility_rules', [])
    decisions = reviews.get('eligibility', {}).get('rules', {})
    available = {item['id'] for item in evidence if item['kind'] == 'eligibility'}
    checks = []
    for index, rule in enumerate(rules, start=1):
        decision = decisions.get(str(index), {})
        status = decision.get('status', 'unknown')
        passed = status == 'pass' and decision.get('evidence_id') in available
        if status == 'pass' and not passed:
            status = 'unknown'
        checks.append({'name':f'Eligibility rule {index}', 'passed':passed,
                       'detail':f'{status.upper()} — {rule} {decision.get("note", "")}'.strip()})
    return checks
