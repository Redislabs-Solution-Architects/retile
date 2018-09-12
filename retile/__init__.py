from os import getcwd
from os.path import join
from shutil import rmtree, move

from retile import mutate, files
from retile.metadata import Metadata
from retile.release import Release
from retile.common import add_label_to_filename

def retile(source, work_dir, **kwargs):
    '''Take input, modify to add label to metadata, create output file'''

    original_context_path = getcwd()

    ##First modify the metadata file and write a new one with a new name containing the label
    
    print 'Creating work dir at ' + work_dir
    files.create_path(work_dir)
    print 'Extracting ' + source + ' to ' + work_dir
    files.unzip(source, work_dir)

    if 'service-broker' not in source:
        slug = 'redis-enterprise'
    else:
        slug = 'redislabs-service-broker'
       
    Metadata(work_dir, **kwargs).mutate(slug)
    Release(work_dir, **kwargs).mutate(source)

    _rebuild_tile(original_context_path, source, work_dir, **kwargs)

    print 'Cleaning Up'
    rmtree(work_dir)

def _rebuild_tile(original_context_path, source, work_dir, label, **kwargs):
    print 'Creating New Tile'
    tile_items = ('metadata', 'migrations', 'releases', 'tile-generator')
    output_file = add_label_to_filename(source, label)
    files.zip_items(output_file, tile_items)
    move(join(work_dir, output_file), join(original_context_path, output_file))
