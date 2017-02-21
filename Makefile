version ?= auto
project ?= betawebreview

deploy:
	cd webreview-fe && ember build && cd ..
	gcloud app deploy \
	  -q \
	  --verbosity=error \
	  --project=$(project) \
	  --version=$(version) \
	  app.yaml
	gcloud app deploy \
	  -q \
	  --verbosity=error \
	  --project=$(project) \
	  --version=$(version) \
	  index.yaml
