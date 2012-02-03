def prepare_test_post_data(test, resource):
    post_data = resource.get_test_post_data()

    if resource.method_requires_auth('POST'):
        logged_in = '_auth_user_id' in test.client.session
        if not logged_in:
            try:
                post_data = resource.setup_post(test, post_data)
            except:
                pass
 
    return post_data
