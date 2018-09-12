from metadata import Metadata

metadata = Metadata('/tmp/retile', 'label')


def test__metadata():
    _metadata = {'name':'name',
                'label':'label',
                'provides_product_versions':[{'name':'name'}],
                'releases':[],
                'property_blueprints':[],
                'job_types':[]}
    
    metadata._mutate_metadata(_metadata)

    assert _metadata['name'] == 'name-label'
    assert _metadata['provides_product_versions'][0]['name'] == 'name-label'
    assert _metadata['label'] == 'label Label'

def test__releases():
    releases = [{'name':'redis-enterprise', 'file':'foo-bar-baz-3243151.23431.31143.pivotal'},
                {'name':'not-redis-enterprise'}]
    metadata._metadata_releases(releases)

    assert releases[0]['file'] == 'foo-bar-label-baz-3243151.23431.31143.pivotal'
    assert releases[0]['name'] == 'redis-enterprise-label'
    assert releases[1] == {'name':'not-redis-enterprise'}

def test__property_blueprints():
    property_blueprints = [{'name':'org', 'default':'foo-bar-baz'},
                           {'name':'redis_api_domain', 'default':'foo.bar.baz'},
                           {'name':'not-relevant-to-us'}]
    metadata._metadata_property_blueprints(property_blueprints)
    
    assert property_blueprints[0]['default'] == 'foo-bar-label-baz'
    assert property_blueprints[1]['default'] == 'foo-label.bar.baz'
    assert property_blueprints[2] == {'name':'not-relevant-to-us'}


def test__release():
    templates = [{'release':'redis-enterprise'}, {'release':'not-redis-enterprise'}]

    metadata._release(templates)

    assert templates[0]['release'] == 'redis-enterprise-label'
    assert templates[1]['release'] == 'not-redis-enterprise'


def test__job_types_manifest():

    jt = {'name':'broker_registrar', 'manifest':'redislabs'}
    metadata._job_types_manifest(jt)
    assert jt['manifest'] == 'redislabs-label'

    jt = {'name':'broker_deregistrar', 'manifest':'redislabs'}
    metadata._job_types_manifest(jt)
    assert jt['manifest'] == 'redislabs-label'

    jt = {'name':'nothing-todo-with-us'}
    _jt = jt.copy()
    metadata._job_types_manifest(jt)
    assert jt == _jt

    jt = {}
    metadata._job_types_manifest(jt)
    assert jt == {}

def run_tests():
    test__job_types_manifest()
    test__release()
    test__property_blueprints()
    test__releases()
    test__metadata()

if __name__ == '__main__':
    run_tests()