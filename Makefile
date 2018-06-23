project ?= webreview
version ?= auto
file ?= app.yaml

create-service-account:
	gcloud --project=$(project) \
	  iam service-accounts create \
	  testing	

create-testing-key:
	gcloud --project=$(project) \
		iam service-accounts keys create \
		--iam-account testing@$(project).iam.gserviceaccount.com \
		testing/service_account_key.json

deploy:
	gcloud app deploy \
			-q \
			--promote \
      --project=$(project) \
      --version=$(version) \
      $(file)
