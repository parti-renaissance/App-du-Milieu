from app.crud import contact

def test_isSubscribed_false():
    """Test that the function isSubscribed returns False when the role is not subscribed to any email list."""
    result = contact.isSubscribed("", [''])
    assert result is False

def test_isSubscribed_false_long_list():
    """Test that the function isSubscribed returns False when the role is not subscribed to any email list, even with a long list of available email lists."""
    result = contact.isSubscribed("", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'subscribed_emails_referents', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is False

def test_isSubscribed_false_unknown_role():
    """Test that the function isSubscribed returns False when the role is unknown, even with a long list of available email lists."""
    result = contact.isSubscribed("fake_role", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'subscribed_emails_referents', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is False

def test_isSubscribed_true():
    """Test that the function isSubscribed returns True when the role is subscribed to at least one email list."""
    result = contact.isSubscribed("referent", ['subscribed_emails_local_host', 'subscribed_emails_movement_information', 'subscribed_emails_weekly_letter', 'subscribed_emails_referents', 'citizen_project_host_email', 'subscribed_emails_citizen_project_creation', 'deputy_email', 'candidate_email', 'senator_email'])
    assert result is True

def test_isSubscribed_true_only_referent():
    """Test that the function isSubscribed returns True when the role is subscribed to only the referents email list."""
    result = contact.isSubscribed("referent", ['subscribed_emails_referents'])
    assert result is True

def test_isSubscribed_false_empty_list():
    """Test that the function isSubscribed returns False when the available email list is empty."""
    result = contact.isSubscribed("referent", [''])
    assert result is False
