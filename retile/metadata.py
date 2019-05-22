from os import unlink
from os.path import join

from retile import files
from retile.common import add_label_to_filename

class Metadata(object):
    def __init__(self, work_dir, label, **kwargs):
        self.work_dir = work_dir
        self.label = label

    def mutate(self, slug):
        # overwrite the metadata file slug here (this only works for tile version 5.4.22000163, should not be a long term fix)
        slug = 'metadata' 
        
        metadata_file = join(self.work_dir, 'metadata', slug + '.yml')
        print 'Importing ' + metadata_file
        metadata = files.import_yaml(metadata_file)
        print 'Mutating Metadata'

        self._mutate_metadata(metadata)

        export_metadata_file = join(self.work_dir, 'metadata', slug + '-' + self.label + '.yml')

        print 'Exporting Mutated Metadata file'
        files.export_yaml(export_metadata_file, metadata)
        print 'Eradicating Old Metadata '+metadata_file
        unlink(metadata_file)

    

    def _mutate_metadata(self, metadata):
        '''Given a parsed metadata/redis-enterprise.yml file, modify it to allow for the tile to run next to another one'''
        
        print 'Changing tile name from ' + metadata['name'] + ' to ' + metadata['name'] + '-' + self.label
        metadata['name'] = metadata['name'] + '-' + self.label

        print 'Changing label from ' + metadata['label'] + ' to ' + metadata['label'] + ' ' + self.label.title()
        metadata['label'] = metadata['label'] + ' ' + self.label.title()

        print 'Changing provides product version name from ' + metadata['provides_product_versions'][0]['name'] + ' to ' + metadata['provides_product_versions'][0]['name'] + '-' + self.label
        metadata['provides_product_versions'][0]['name'] = metadata['provides_product_versions'][0]['name'] + '-' + self.label

        print 'Mutating Release Info'
        self._metadata_releases(metadata['releases'])
        print 'Mutating Property Blueprints'
        self._metadata_property_blueprints(metadata['property_blueprints'])
        print 'Mutating Job Types'
        self._job_types(metadata['job_types'])

    def _metadata_releases(self, releases):
        '''
        Given a release obj from a metadata/redis-enterprise.yml file,
        update the releases filename and name to include the label in the appropriate place
        '''

        for release in releases:
            if release.get('name') in ('redis-enterprise', 'redislabs-service-broker'):
                print 'Changing release name from ' + release['name'] + ' to ' + release['name'] + '-' + self.label
                release['name'] = release['name'] + '-' + self.label
                print 'Changing release file name from ' + release['file'] + ' to ' + add_label_to_filename(release['file'], self.label)
                release['file'] = add_label_to_filename(release['file'], self.label)

    def _metadata_property_blueprints(self, pb):
        '''
        Given a property blueprints obj from a metadata/redis-enterprise.yml file
        update property defaults that would clash with other installs by adding a . or - and the label
        depending on what the property is
        '''

        props_to_mutate = ('org', 'space', 'redis_broker_domain', 'redis_api_domain', 'redis_console_domain')
        for prop in pb:
            if prop['name'] in props_to_mutate:
                # dots vs dashes
                if 'domain' in prop['name']:
                    domain_name = prop['default'].split('.')
                    domain_name[0] = domain_name[0] + '-' + self.label
                    prop['default'] = '.'.join(domain_name)
                else:
                    name = prop['default'].split('-')
                    name.insert(2, self.label)
                    prop['default'] = '-'.join(name)

    def _job_types(self, jts):
        for jt in jts:
            self._release(jt['templates'])
            self._job_types_manifest(jt)

    def _release(self, templates):
        '''
        Given a list of releases from a job type obj from a metadata/redis-enterprise.yml file
        update release from 'redis-enterprise' to 'redis-enterprise-LABEL'
        '''
        
        for template in templates:
            if template['release'] in ('redis-enterprise', 'redislabs-service-broker'):
                template['release'] = template['release'] + '-' + self.label

    def _job_types_manifest(self, jt):
        '''
        Given a job type object from a metadata/redis-enterprise.yml file
        update various values in the manifest depending on which job it is
        '''

        if jt.get('name') in ('broker_registrar', 'broker_deregistrar'): 
            jt['manifest'] = jt['manifest'].replace('redislabs', 'redislabs-' + self.label)
