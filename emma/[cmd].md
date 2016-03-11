# Nginx

sudo cp nginx/emma.conf /etc/nginx/apps && sudo service nginx reload

# Solr

python manage.py rebuild_index
python manage.py update_index

## Build Solr schema, sync Solr config, reload core

python manage.py build_solr_schema --filename=/var/solr/data/emma/conf/schema.xml && rsync --exclude=solr.xml templates/search_configuration/* /var/solr/data/emma/conf && curl 'http://localhost:8983/solr/admin/cores?action=RELOAD&core=emma&wt=json&indent=true'

## Build Solr schema, sync Solr config, reload core + rebuild index

python manage.py build_solr_schema --filename=/var/solr/data/emma/conf/schema.xml && rsync --exclude=solr.xml templates/search_configuration/* /var/solr/data/emma/conf && curl 'http://localhost:8983/solr/admin/cores?action=RELOAD&core=emma&wt=json&indent=true' && python manage.py rebuild_index
