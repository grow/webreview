version ?= auto
project ?= betawebreview

run-frontend:
	cd webreview-fe && ember serve

run-backend:
	virtualenv env
	. env/bin/activate
	dev_appserver.py \
		--port=8088 .

install:
	virtualenv env
	. env/bin/activate
	./env/bin/pip install \
	  --upgrade \
	  --allow-unverified dateutil \
	  --allow-external dateutil \
	  -r \
	  requirements.txt
	./env/bin/gaenv --lib lib --no-import
	
test:
	. env/bin/activate
	./env/bin/nosetests \
	  -v \
	  --rednose \
	  --nocapture \
	  --with-gae \
	  --gae-lib-root=$(HOME)/google_appengine \
	  --with-coverage \
	  --cover-erase \
	  --cover-html \
	  --cover-html-dir=htmlcov \
	  --cover-package=app \
	  app/

deploy:
	$(MAKE) test
	cd webreview-fe && ember build && cd ..
	gcloud app deploy \
		-q \
		--verbosity=error \
		--project=$(project) \
		--version=$(version) \
		--no-promote \
		app.yaml
	gcloud app deploy \
		-q \
		--no-promote \
		--verbosity=error \
		--project=$(project) \
		--version=$(version) \
		index.yaml
