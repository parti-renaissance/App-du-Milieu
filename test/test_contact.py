from app.crud import contact

def test_isSubscribed_1():
    result = contact.isSubscribed("", [''])
    assert result is False

def test_isSubscribed_2():
    result = contact.isSubscribed("", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'subscribed_emails_referents', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is False

def test_isSubscribed_3():
    result = contact.isSubscribed("fake_role", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'subscribed_emails_referents', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is False

def test_isSubscribed_4():
    result = contact.isSubscribed("referent", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'subscribed_emails_referents', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is True

def test_isSubscribed_5():
    result = contact.isSubscribed("referent", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is False

def test_isSubscribed_6():
    result = contact.isSubscribed("referent", ['subscribed_emails_referents'])
    assert result is True

def test_isSubscribed_7():
    result = contact.isSubscribed("referent", [''])
    assert result is False
