version ?= auto
project ?= betawebreview

deploy:
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
