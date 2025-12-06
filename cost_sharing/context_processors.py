from .models import CostSharingAgreement

def accepted_agreement(request):
    """
    Adds has_accepted_agreement (bool) and accepted_agreement_id (int|None)
    to template context for authenticated students.
    """
    has = False
    ag_id = None
    user = getattr(request, 'user', None)
    if user and user.is_authenticated and getattr(user, 'role', None) == 'student':
        ag = CostSharingAgreement.objects.filter(student=user, status__iexact='accepted').order_by('-id').first()
        if ag:
            has = True
            ag_id = ag.id
    return {
        'has_accepted_agreement': has,
        'accepted_agreement_id': ag_id,
    }
